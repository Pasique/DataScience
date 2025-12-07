import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
DB_PATH = "sqlite:///credit_risk.db"
CHROMA_PATH = "./chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

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
    # LangGraph espera uma lista de mensagens
    inputs = {"messages": [("user", query_text)]}
    
    # O output contém o estado final, incluindo as mensagens
    result = agent.invoke(inputs)
    
    # A última mensagem é a resposta do assistente
    last_message = result["messages"][-1]
    print(f"Answer: {last_message.content}")

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
