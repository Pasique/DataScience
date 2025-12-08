import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Configurações
PERSIST_DIRECTORY = "./chroma_db"
DOCS_DIR = "."
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def setup_vectorstore():
    print("Iniciando ingestão de documentos para RAG...")
    
    # 1. Carregar Documentos
    documents = []
    for filename in ["politica_risco.md", "glossario.md"]:
        file_path = os.path.join(DOCS_DIR, filename)
        if os.path.exists(file_path):
            print(f"Carregando {filename}...")
            loader = TextLoader(file_path)
            documents.extend(loader.load())
        else:
            print(f"AVISO: {filename} não encontrado.")
    
    if not documents:
        print("Nenhum documento carregado. Abortando.")
        return

    # 2. Splitter (Chunking)
    # Por que RecursiveCharacterTextSplitter?
    # Ele tenta manter parágrafos e frases juntos, respeitando a estrutura semântica do texto.
    # Chunk size de 1000 caracteres com overlap de 200 é um padrão inicial robusto.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n## ", "\n\n", "\n", " ", ""]
    )
    splits = text_splitter.split_documents(documents)
    print(f"Documentos divididos em {len(splits)} chunks.")

    # 3. Embeddings & Vector Store
    # Por que HuggingFaceEmbeddings (all-MiniLM-L6-v2)?
    # Modelo leve, rápido e com ótima performance para inglês/português em tarefas gerais.
    # Roda localmente (CPU friendly), ideal para dev/portfolio sem custos de API.
    print(f"Gerando embeddings com {EMBEDDING_MODEL}...")
    embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    # Criação do banco vetorial persistente
    if os.path.exists(PERSIST_DIRECTORY):
        print(f"Atualizando banco existente em {PERSIST_DIRECTORY}...")
    else:
        print(f"Criando novo banco em {PERSIST_DIRECTORY}...")
        
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embedding_function,
        persist_directory=PERSIST_DIRECTORY
    )
    
    # Em versões recentes do Chroma, a persistência é automática, mas chamar persist() garante compatibilidade.
    # vectorstore.persist() 
    
    print("Ingestão concluída com sucesso!")
    
    # Teste rápido de recuperação
    print("\n--- Teste de Recuperação (Sanity Check) ---")
    query = "Qual a taxa de juros para score baixo?"
    docs = vectorstore.similarity_search(query, k=2)
    for i, doc in enumerate(docs):
        print(f"\nResultado {i+1}:")
        print(doc.page_content[:200] + "...")

if __name__ == "__main__":
    # Garante que estamos rodando no diretório correto
    if os.path.basename(os.getcwd()) != "FinSight":
        print("Por favor, execute este script de dentro da pasta 'FinSight'.")
    else:
        setup_vectorstore()
