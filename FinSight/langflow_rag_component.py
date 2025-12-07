from langflow.custom import CustomComponent
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.tools import Tool
import os

class FinSightRAGTool(CustomComponent):
    display_name = "FinSight RAG Tool"
    description = "Ferramenta de busca nas políticas de risco do FinSight (Local ChromaDB)."
    
    def build_config(self):
        return {
            "chroma_path": {"display_name": "ChromaDB Path", "value": "./chroma_db"},
            "embedding_model": {"display_name": "Embedding Model", "value": "sentence-transformers/all-MiniLM-L6-v2"},
        }

    def build(self, chroma_path: str, embedding_model: str) -> Tool:
        # Configurar Embeddings
        embedding_function = HuggingFaceEmbeddings(model_name=embedding_model)
        
        # Carregar Vector Store
        # Nota: O caminho deve ser absoluto ou relativo ao diretório de execução do LangFlow
        if not os.path.isabs(chroma_path):
            chroma_path = os.path.abspath(chroma_path)
            
        vectorstore = Chroma(
            persist_directory=chroma_path, 
            embedding_function=embedding_function
        )
        
        def query_policy(query: str) -> str:
            """Consulta as políticas de risco e glossário."""
            try:
                docs = vectorstore.similarity_search(query, k=3)
                return "\n\n".join([d.page_content for d in docs])
            except Exception as e:
                return f"Erro ao consultar RAG: {str(e)}"

        rag_tool = Tool(
            name="search_policy_and_glossary",
            func=query_policy,
            description="Útil para responder perguntas sobre regras de negócio, políticas de risco, faixas de score e definições de termos. Use isso ANTES de consultar o banco de dados se a pergunta envolver regras."
        )
        
        return rag_tool
