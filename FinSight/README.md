# FinSight - Agente de Análise de Risco de Crédito

O **FinSight** é um agente inteligente projetado para auxiliar na análise de risco de crédito. Ele combina a capacidade de consultar dados estruturados de clientes (SQL) com a análise de políticas de risco não estruturadas (RAG em documentos Markdown), utilizando modelos de linguagem (LLMs) para fornecer recomendações embasadas.

##  Funcionalidades

*   **Análise de Dados Estruturados (SQL):** Consulta saldo, renda, score de crédito e histórico de transações em um banco de dados SQLite local.
*   **RAG (Retrieval-Augmented Generation):** Consulta políticas de risco e glossários financeiros armazenados em um banco vetorial (ChromaDB) para validar regras de negócio.
*   **Agente Híbrido:** Um orquestrador inteligente decide quando usar SQL, quando usar RAG, ou quando combinar ambos para responder a perguntas complexas (ex: "O cliente X tem renda compatível com a política de risco para um empréstimo de Y?").
*   **Interface Visual (LangFlow):** Suporte para construção e execução do agente através de uma interface visual low-code.

##  Instalação

1.  **Pré-requisitos:**
    *   Python 3.10+ (Testado com Python 3.13)
    *   Chave de API da OpenAI

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuração de Ambiente:**
    Crie um arquivo `.env` na raiz do projeto com sua chave da OpenAI:
    ```env
    OPENAI_API_KEY=sk-...
    ```

##  Como Executar

### Opção 1: Interface Visual (LangFlow) - **Recomendado**
Devido a incompatibilidades conhecidas entre versões recentes do Python (3.13) e o FastAPI/LangFlow, incluímos um script de correção.

1.  Execute o script de inicialização:
    ```bash
    python run_langflow_fix.py
    ```
2.  Acesse no navegador: `http://localhost:7861` (ou a porta indicada no terminal).

**Configurando no LangFlow:**
*   Crie um novo projeto.
*   Adicione um **Agent** (ex: OpenAI Tools Agent).
*   Adicione o componente **SQLDatabase** apontando para `sqlite:///credit_risk.db`.
*   Adicione um **Custom Component** para o RAG:
    *   Copie o código de `langflow_rag_component.py`.
    *   Cole no editor do componente customizado.
*   Conecte as ferramentas ao agente e use o **Chat Input/Output** para interagir.

### Opção 2: Linha de Comando (CLI)
Para interagir com o agente diretamente pelo terminal:

```bash
python agent.py
```
O agente iniciará um loop interativo onde você pode fazer perguntas como:
*   "Qual o saldo do cliente João Silva?"
*   "Quais são as regras para aprovação de crédito imobiliário?"
*   "O cliente Maria Souza pode financiar um imóvel de 500 mil?"

##  Estrutura do Projeto

*   **`run_langflow_fix.py`**: Script principal para iniciar o LangFlow (com patches para Python 3.13).
*   **`agent.py`**: Implementação do agente em código puro (Python + LangGraph).
*   **`langflow_rag_component.py`**: Componente customizado para integrar o ChromaDB local ao LangFlow.
*   **`credit_risk.db`**: Banco de dados SQLite com dados sintéticos de clientes.
*   **`chroma_db/`**: Banco vetorial contendo os embeddings das políticas de risco.
*   **`setup_files/`**: Scripts utilizados para gerar os dados e popular os bancos.
    *   `setup_data.py`: Gera dados fictícios e cria o `credit_risk.db`.
    *   `setup_vectorstore.py`: Lê os markdowns e popula o `chroma_db`.
    *   `politica_risco.md` / `glossario.md`: Documentos originais de conhecimento.

##  Regenerando os Dados (Opcional)
Se precisar resetar o banco de dados ou atualizar as políticas:

1.  Entre na pasta de setup:
    ```bash
    cd setup_files
    ```
2.  Execute os scripts (ajuste os caminhos de saída se necessário, pois eles foram movidos):
    *   *Nota: Os scripts podem precisar de ajustes de importação/caminho se rodados de dentro da subpasta.*

---
**FinSight** - Inteligência Artificial para Análise de Crédito.
