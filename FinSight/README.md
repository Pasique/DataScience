# FinSight AI - Sistema Inteligente de Análise de Risco de Crédito

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-1.1+-green.svg)](https://langchain.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.52+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**FinSight** é um assistente de IA especializado em análise de risco de crédito que combina o poder de agentes autônomos, RAG (Retrieval-Augmented Generation) e consultas SQL para fornecer análises precisas e contextualizadas sobre dados financeiros.

## Destaques

- **Agente Híbrido Inteligente**: Combina SQL e RAG para decisões contextualizadas
- **Guardrails Avançados**: Sistema de moderação para bloquear conteúdo inadequado
- **Interface Web Moderna**: Chat interativo via Streamlit
- **Dados Sintéticos Realistas**: 500 clientes com scores, rendas e histórico
- **RAG com ChromaDB**: Políticas de risco e glossário financeiro indexados
- **LangGraph**: Orquestração inteligente de ferramentas

## Funcionalidades Principais

### 1. Consulta SQL Inteligente
Pergunte sobre dados de clientes e o agente consulta automaticamente o banco:
- "Quantos clientes temos em São Paulo?"
- "Qual a renda média dos clientes com score acima de 700?"
- "Liste os clientes da Faixa A de risco"

### 2. RAG (Retrieval-Augmented Generation)
Consulta políticas e glossário para contexto de negócio:
- "Qual a taxa de juros para score 600?"
- "O que significa Faixa de Risco?"
- "Quais as regras para aprovação de crédito?"

### 3. Análise Híbrida
Combina múltiplas fontes para respostas complexas:
- "Quantos clientes do RJ se qualificam para a menor taxa de juros?"
- "Qual estado tem o melhor perfil de risco?"

### 4. Guardrails de Segurança
Bloqueia automaticamente:
- Linguagem ofensiva
- Assuntos polêmicos (política, religião)
- Perguntas fora do contexto financeiro

## Instalação

### Pré-requisitos
- Python 3.10+ (testado com 3.13)
- Chave de API da OpenAI

### Passo a Passo

1. **Clone o repositório**
```bash
git clone https://github.com/Pasique/DataScience.git
cd DataScience/FinSight
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Configure a API Key**
Crie um arquivo `.env` na raiz do projeto:
```env
OPENAI_API_KEY=sua-chave-aqui
```

4. **Gere os dados (primeira execução)**
```bash
python setup_files/setup_data.py
python setup_files/setup_vectorstore.py
```

## Como Usar

### Interface Web (Recomendado)

Execute o aplicativo Streamlit:
```bash
streamlit run app.py
# ou
python -m streamlit run app.py
```

Acesse no navegador: `http://localhost:8501`

### Linha de Comando

Execute testes diretos no terminal:
```bash
python agent.py
```

## Estrutura do Projeto

```
FinSight/
├── app.py                          # Interface Streamlit
├── agent.py                        # Agente principal (LangGraph)
├── guardrails.py                   # Sistema de moderação
├── requirements.txt                # Dependências
├── .env                           # Configurações (criar manualmente)
├── credit_risk.db                 # Banco de dados SQLite
├── chroma_db/                     # Vector store (ChromaDB)
├── setup_files/
│   ├── setup_data.py              # Gerador de dados sintéticos
│   ├── setup_vectorstore.py       # Popula o ChromaDB
│   ├── politica_risco.md          # Políticas de crédito
│   └── glossario.md               # Termos financeiros
└── README.md
```

## Exemplos de Perguntas

### Consultas SQL
```
"Quantos clientes temos no estado de SP?"
"Qual a média de renda dos clientes com score acima de 700?"
"Mostre a distribuição de clientes por faixa de score"
```

### Consultas RAG
```
"Qual a taxa de juros para a Faixa C?"
"O que é Score de Crédito?"
"Quais são todas as faixas de risco?"
```

### Consultas Híbridas
```
"Quantos clientes da Faixa A temos na base?"
"Dos clientes de MG, quantos se qualificariam para a Faixa B?"
"Qual percentual dos clientes está na faixa de maior risco?"
```

### Testes de Guardrails (Serão Bloqueadas)
```
"Qual sua opinião sobre política?"
"Me ensine a fazer um bolo"
"Quando começou a revolução francesa?"
```

## Tecnologias Utilizadas

- **LangChain**: Framework para aplicações com LLM
- **LangGraph**: Orquestração de agentes e fluxos
- **OpenAI GPT-4o-mini**: Modelo de linguagem
- **ChromaDB**: Vector database para RAG
- **Streamlit**: Interface web interativa
- **SQLite**: Banco de dados relacional
- **Sentence Transformers**: Embeddings locais
- **Faker**: Geração de dados sintéticos

## Arquitetura

```
┌─────────────┐
│   Usuário   │
└──────┬──────┘
       │
┌──────▼──────────┐
│   Streamlit UI  │
└──────┬──────────┘
       │
┌──────▼──────────┐
│   Guardrails    │ ◄── Filtra entradas inadequadas
└──────┬──────────┘
       │
┌──────▼──────────┐
│  Agent (LLM)    │
└─┬────────────┬──┘
  │            │
┌─▼───────┐  ┌─▼──────┐
│SQL Tool │  │RAG Tool│
│(SQLite) │  │(Chroma)│
└─────────┘  └────────┘
```

## Regenerando os Dados

Para resetar o banco de dados ou atualizar as políticas:

```bash
cd setup_files
python setup_data.py           # Gera novo banco SQLite
python setup_vectorstore.py    # Atualiza ChromaDB
```

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir melhorias
- Enviar pull requests

## Licença

Este projeto é open source e está disponível sob a licença MIT.

## Autor

**Paulo Siqueira**
- GitHub: [@Pasique](https://github.com/Pasique)
- LinkedIn: [Paulo Siqueira](https://linkedin.com/in/seu-perfil)

## Agradecimentos

- OpenAI pela API
- LangChain pela framework
- Comunidade open source

---

**FinSight AI** - Transformando dados em decisões inteligentes
