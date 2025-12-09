import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent
from guardrails import FinSightGuardrails
from metrics import MetricsCollector

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar coletor de métricas
metrics_collector = MetricsCollector()

# Configurações
DB_PATH = "sqlite:///data/credit_risk.db"
CHROMA_PATH = "./data/chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Inicializar Guardrails
guardrails = FinSightGuardrails()

def get_agent():
    # 1. LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # 2. Ferramenta SQL
    db = SQLDatabase.from_uri(DB_PATH)
    sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    sql_tools = sql_toolkit.get_tools()

    # 3. Ferramenta RAG (Vector Store)
    embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    
    def query_policy(query: str) -> str:
        """Consulta as políticas de risco e glossário."""
        docs = vectorstore.similarity_search(query, k=3)
        return "\n\n".join([d.page_content for d in docs])

    rag_tool = Tool(
        name="search_policy_and_glossary",
        func=query_policy,
        description="Útil para responder perguntas sobre regras de negócio, políticas de risco, faixas de score e definições de termos. Use isso ANTES de consultar o banco de dados se a pergunta envolver regras."
    )

    # 4. Combinar Ferramentas
    tools = sql_tools + [rag_tool]

    # 5. Criar Agente (LangGraph)
    # O create_react_agent do LangGraph já cria um grafo executável
    agent_executor = create_react_agent(llm, tools)
    
    return agent_executor

def run_query(agent, query_text):
    print(f"\nQuestion: {query_text}")
    
    start_time = time.time()
    query_type = None
    success = True
    error_msg = None
    blocked_reason = None
    
    # 1. Guardrails Check
    print("  [Guardrails] Verificando segurança e relevância...")
    check_result = guardrails.check_input(query_text)
    
    if check_result != "ALLOWED":
        print(f"  [Guardrails] BLOQUEADO: {check_result}")
        response_time = time.time() - start_time
        
        # Log métrica de bloqueio
        metrics_collector.log_query(
            query=query_text,
            query_type="blocked",
            response_time=response_time,
            tokens_used=50,  # Estimativa baixa para guardrails
            success=False,
            blocked_reason=check_result
        )
        return

    print("  [Guardrails] Aprovado. Processando...")

    try:
        # LangGraph espera uma lista de mensagens
        inputs = {"messages": [("user", query_text)]}
        
        # O output contém o estado final, incluindo as mensagens
        result = agent.invoke(inputs)
        
        # A última mensagem é a resposta do assistente
        last_message = result["messages"][-1]
        response = last_message.content
        print(f"Answer: {response}")
        
        # Detectar tipo de query de forma mais precisa
        # Analisar as mensagens intermediárias para ver quais tools foram usados
        query_type = "unknown"
        used_sql = False
        used_rag = False
        
        # Verificar mensagens do agente para identificar tools usados
        for msg in result["messages"]:
            msg_str = str(msg).lower()
            if "sql_db" in msg_str or "list_tables" in msg_str or "query_sql" in msg_str:
                used_sql = True
            if "search_policy" in msg_str or "glossary" in msg_str or "política" in msg_str:
                used_rag = True
        
        # Classificar baseado nos tools usados
        if used_sql and used_rag:
            query_type = "hybrid"
        elif used_sql:
            query_type = "sql"
        elif used_rag:
            query_type = "rag"
        else:
            # Fallback: analisar a resposta
            response_lower = response.lower()
            if any(word in response_lower for word in ["select", "database", "tabela", "coluna"]):
                query_type = "sql"
            elif any(word in response_lower for word in ["política", "faixa", "glossário", "score de crédito"]):
                query_type = "rag"
            else:
                query_type = "hybrid"
        
        # Estimativa de tokens (aproximada)
        tokens_used = len(query_text.split()) * 1.3 + len(response.split()) * 1.3
        tokens_used = int(tokens_used * 100)  # Fator de conversão aproximado
        
    except Exception as e:
        success = False
        error_msg = str(e)
        query_type = "error"
        tokens_used = 100
        print(f"  [ERRO] {error_msg}")
    
    response_time = time.time() - start_time
    
    # Log métrica
    metrics_collector.log_query(
        query=query_text,
        query_type=query_type or "unknown",
        response_time=response_time,
        tokens_used=tokens_used,
        success=success,
        error=error_msg
    )

if __name__ == "__main__":
    print("Inicializando Agente FinSight (Híbrido SQL + RAG - Powered by LangGraph)...")
    agent = get_agent()
    
    print("\n--- Exemplo 1: Pergunta de Regra de Negócio (RAG) ---")
    run_query(agent, "Qual a taxa de juros para um cliente com Score 600 (Faixa C)?")
    
    print("\n--- Exemplo 2: Pergunta de Dados (SQL) ---")
    run_query(agent, "Quantos clientes temos no estado de SP?")

    print("\n--- Exemplo 3: Pergunta Híbrida (Complexa) ---")
    # O agente precisa saber o que é "Faixa A" (RAG) para depois filtrar no banco (SQL)
    run_query(agent, "Quantos clientes da Faixa A (Excelente) nós temos na base? Consulte a política para saber o range de score.")

    print("\n--- Exemplo 4: Teste de Guardrails (Off-topic) ---")
    run_query(agent, "Em que ano começou a revolução francesa?")
