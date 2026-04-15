import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent
from guardrails import FinSightGuardrails
from metrics import MetricsCollector

load_dotenv()

metrics_collector = MetricsCollector()

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = f"sqlite:///{_BASE_DIR}/data/credit_risk.db"
CHROMA_PATH = os.path.join(_BASE_DIR, "data", "chroma_db")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

guardrails = FinSightGuardrails()

# Cache do agente para evitar reinicializações
_agent_cache = None

def get_agent():
    """Inicializa o agente híbrido SQL + RAG com cache."""
    global _agent_cache
    
    if _agent_cache is not None:
        return _agent_cache
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Setup do banco SQL
    db = SQLDatabase.from_uri(DB_PATH)
    sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    sql_tools = sql_toolkit.get_tools()

    # Setup do RAG
    embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    
    def query_policy(query: str) -> str:
        """Busca políticas e glossário relevantes."""
        docs = vectorstore.similarity_search(query, k=3)
        return "\n\n".join([d.page_content for d in docs])

    rag_tool = Tool(
        name="search_policy_and_glossary",
        func=query_policy,
        description="Busca informações sobre políticas de risco, faixas de score e termos financeiros. Use antes de consultar o banco se a pergunta envolver regras de negócio."
    )

    tools = sql_tools + [rag_tool]
    agent_executor = create_react_agent(llm, tools)
    
    _agent_cache = agent_executor
    return agent_executor

def run_query(agent, query_text):
    """Executa uma query com guardrails e coleta de métricas."""
    print(f"\nQuestion: {query_text}")
    
    start_time = time.time()
    query_type = None
    success = True
    error_msg = None
    
    print("  [Guardrails] Verificando...")
    check_result = guardrails.check_input(query_text)
    
    if check_result != "ALLOWED":
        print(f"  [Guardrails] BLOQUEADO: {check_result}")
        response_time = time.time() - start_time
        
        metrics_collector.log_query(
            query=query_text,
            query_type="blocked",
            response_time=response_time,
            tokens_used=50,
            success=False,
            blocked_reason=check_result,
            sql_query=None
        )
        return

    print("  [Guardrails] OK. Processando...")

    try:
        inputs = {"messages": [("user", query_text)]}
        result = agent.invoke(inputs)
        
        last_message = result["messages"][-1]
        response = last_message.content
        print(f"Answer: {response}")
        
        # Identifica tipo de query pelos tools usados e extrai SQL
        used_sql = False
        used_rag = False
        sql_query = None
        
        for msg in result["messages"]:
            msg_str = str(msg).lower()
            if any(term in msg_str for term in ["sql_db", "list_tables", "query_sql"]):
                used_sql = True
                # Tenta extrair query SQL
                if "select" in msg_str:
                    # Procura por SELECT queries
                    content = str(msg)
                    import re
                    sql_pattern = r"(SELECT\s+.*?)(?:;|\n|$|'|\")"
                    matches = re.findall(sql_pattern, content, re.IGNORECASE | re.DOTALL)
                    if matches:
                        sql_query = matches[0].strip()
            if any(term in msg_str for term in ["search_policy", "glossary", "política"]):
                used_rag = True
        
        if used_sql and used_rag:
            query_type = "hybrid"
        elif used_sql:
            query_type = "sql"
        elif used_rag:
            query_type = "rag"
        else:
            query_type = "unknown"
        
        # Estimativa de tokens
        tokens_used = len(query_text.split()) * 1.3 + len(response.split()) * 1.3
        tokens_used = int(tokens_used * 100)
        
    except Exception as e:
        success = False
        error_msg = str(e)
        query_type = "error"
        tokens_used = 100
        print(f"  [ERRO] {error_msg}")
    
    response_time = time.time() - start_time
    
    metrics_collector.log_query(
        query=query_text,
        query_type=query_type or "unknown",
        response_time=response_time,
        tokens_used=tokens_used,
        success=success,
        error=error_msg,
        sql_query=sql_query if 'sql_query' in locals() else None
    )

if __name__ == "__main__":
    print("FinSight Agent - Teste de Funcionalidades\n")
    agent = get_agent()
    
    print("\n=== Teste 1: RAG (Políticas) ===")
    run_query(agent, "Qual a taxa de juros para um cliente com Score 600?")
    
    print("\n=== Teste 2: SQL (Dados) ===")
    run_query(agent, "Quantos clientes temos no estado de SP?")

    print("\n=== Teste 3: Híbrido ===")
    run_query(agent, "Quantos clientes da Faixa A temos na base?")

    print("\n=== Teste 4: Guardrails ===")
    run_query(agent, "Em que ano começou a revolução francesa?")
