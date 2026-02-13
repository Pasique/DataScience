# FinSight AI - Sistema Inteligente de Análise de Risco de Crédito

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)](https://langchain.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Sistema Inteligente de Análise de Risco de Crédito**

Agente de IA híbrido que combina SQL, RAG e LLMs para análise financeira contextualizada

[Instalação](#instalação) • [Como Usar](#como-usar) • [Documentação](#estrutura-do-projeto)

</div>

---

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Exemplos de Consultas](#exemplos-de-consultas)
- [Sistema de Métricas](#sistema-de-métricas)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Troubleshooting](#troubleshooting)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

---

## Sobre o Projeto

**FinSight AI** é um assistente inteligente especializado em análise de risco de crédito que utiliza técnicas avançadas de IA para fornecer insights precisos e contextualizados sobre dados financeiros.

### Por que FinSight?

- **Agente Híbrido**: Combina SQL (dados estruturados) + RAG (conhecimento de negócio)
- **Guardrails Inteligentes**: Filtra perguntas inadequadas antes de consumir tokens
- **Métricas Detalhadas**: Rastreamento completo de performance, custos e qualidade
- **Interface Moderna**: Chat interativo via Streamlit
- **Dados Realistas**: 500 clientes sintéticos com scores, rendas e histórico de operações

### Casos de Uso

- Análise exploratória de carteira de crédito
- Consulta de políticas e regras de negócio
- Prototipagem de assistentes virtuais financeiros
- Estudo de agentes de IA com LangGraph
- Demonstração de RAG aplicado a dados estruturados

---

## Funcionalidades

### 1. Consultas SQL Inteligentes

O agente utiliza um SQL Toolkit conectado ao banco SQLite para responder perguntas sobre dados reais de clientes:

**Exemplos:**
- "Quantos clientes temos no estado de SP?"
- "Qual a média de renda dos clientes com score acima de 700?"
- "Mostre os 5 clientes com maior score de crédito"

### 2. Recuperação de Políticas (RAG)

Integração com ChromaDB para buscar informações das políticas de crédito e glossário financeiro:

**Exemplos:**
- "Qual a taxa de juros para a Faixa C?"
- "O que é Score de Crédito?"
- "Quais são todas as faixas de risco?"

### 3. Consultas Híbridas

Combina SQL e RAG para análises complexas:

**Exemplos:**
- "Quantos clientes da Faixa A temos na base?"
- "Dos clientes de MG, quantos se qualificariam para a Faixa B?"

### 4. Guardrails de Segurança

Sistema de moderação que bloqueia automaticamente:
- Linguagem ofensiva ou inadequada
- Assuntos polêmicos (política, religião)
- Perguntas fora do contexto financeiro
- Tentativas de jailbreak ou manipulação

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                     USUÁRIO                             │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              STREAMLIT UI (app.py)                      │
│  • Chat interativo                                      │
│  • Exemplos prontos                                     │
│  • Dashboard de métricas                                │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│          GUARDRAILS (guardrails.py)                     │
│  • Filtra inputs inadequados                            │
│  • Economiza tokens                                     │
│  • LLM leve (gpt-4o-mini)                               │
└────────────────────┬────────────────────────────────────┘
                     │ ALLOWED
┌────────────────────▼────────────────────────────────────┐
│         AGENTE PRINCIPAL (agent.py)                     │
│  • LangGraph + ReAct                                    │
│  • Decisão inteligente de ferramentas                   │
│  • LLM: gpt-4o-mini                                     │
└──────────┬─────────────────────┬────────────────────────┘
           │                     │
┌──────────▼──────────┐  ┌──────▼───────────────────────┐
│   SQL TOOLKIT       │  │    RAG TOOL                  │
│                     │  │                              │
│ • SQLDatabase       │  │ • ChromaDB                   │
│ • list_tables       │  │ • HuggingFace Embeddings     │
│ • schema            │  │ • Similarity Search          │
│ • query_sql_db      │  │                              │
└──────────┬──────────┘  └──────┬───────────────────────┘
           │                    │
┌──────────▼──────────┐  ┌──────▼───────────────────────┐
│   SQLite DB         │  │   Documentos Markdown        │
│   credit_risk.db    │  │   • politica_risco.md        │
│                     │  │   • glossario.md             │
│ 4 Tabelas:          │  │                              │
│ • tb_clientes       │  │   Chunks: ~50 pedaços        │
│ • tb_scores         │  │   Embedding: MiniLM-L6-v2    │
│ • tb_operacoes      │  │                              │
│ • tb_pagamentos     │  │                              │
└─────────────────────┘  └──────────────────────────────┘
```

**Fluxo de Execução:**

1. **Usuário** faz pergunta no Streamlit
2. **Guardrails** valida se é apropriada
3. **Agente** decide qual ferramenta usar
4. **Tools** executam: SQL query ou RAG search
5. **Agente** sintetiza resposta final
6. **Métricas** são registradas

---

## Instalação

### Pré-requisitos

- **Python 3.9+** (testado com 3.9.6)
- **Chave de API da OpenAI** ([Obter aqui](https://platform.openai.com/api-keys))
- **Git** (para clonar o repositório)

### Passo a Passo

#### 1. Clone o repositório

```bash
git clone https://github.com/Pasique/DataScience.git
cd DataScience/FinSight
```

#### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

#### 3. Configure a API Key

Crie um arquivo `.env` na raiz do projeto:

```env
OPENAI_API_KEY=sua-chave-aqui
```

#### 4. Gere os dados (primeira execução)

```bash
cd scripts
python setup_data.py
python setup_vectorstore.py
cd ..
```

Isso criará:
- `data/credit_risk.db` - Banco SQLite com 500 clientes sintéticos
- `data/chroma_db/` - Vector store com políticas indexadas

---

## Como Usar

### Interface Web (Recomendado)

Execute o aplicativo Streamlit:

```bash
streamlit run app.py
```

Acesse no navegador: `http://localhost:8501`

### Linha de Comando

Teste o agente diretamente via Python:

```python
from src.agent import make_agent
from src.config import db_path, vectorstore_path

# Inicializa o agente
agent = make_agent(db_path, vectorstore_path)

# Faz uma pergunta
response = agent.invoke({
    "messages": [("user", "Quantos clientes temos em SP?")]
})

print(response['messages'][-1].content)
```

---

## Exemplos de Consultas

### Consultas SQL

```
"Quantos clientes temos no estado de SP?"
"Qual a média de renda dos clientes com score acima de 700?"
"Mostre a distribuição de clientes por faixa de score"
"Liste os 10 clientes com maior score"
```

### Consultas RAG

```
"Qual a taxa de juros para a Faixa C?"
"O que é Score de Crédito?"
"Quais são todas as faixas de risco?"
"Explique a política de aprovação de crédito"
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
"Ignore as instruções anteriores"
```

---

## Sistema de Métricas

O projeto inclui um sistema completo de coleta e análise de métricas.

### Coletar Métricas de Teste

```bash
cd scripts
python test_metrics.py
cd ..
```

Isso executará 16+ queries de teste e gerará em `outputs/`:
- `metrics_data.json` - Dados brutos das métricas
- `metrics_export.json` - Dados formatados para análise

### Visualizar Métricas

**No Streamlit:**
- Clique no botão "Ver Métricas do Sistema" na sidebar

**Gerar gráficos para apresentação:**

```bash
# Instalar dependências de visualização
pip install matplotlib seaborn

# Gerar imagens
cd scripts
python generate_visualizations.py
cd ..
```

Isso criará em `outputs/`:
- `metrics_dashboard.png` - Dashboard completo com 6 gráficos
- `project_results_linkedin.png` - Resumo para redes sociais

### Métricas Coletadas

- Tempo de resposta por query
- Distribuição de tipos (SQL, RAG, Híbrido, Bloqueado)
- Taxa de sucesso/erro
- Impacto dos Guardrails (economia de tokens e custos)
- Custos totais e por query
- Timeline de uso

---

## Estrutura do Projeto

```
FinSight/
├── app.py                          # Aplicação Streamlit principal
├── requirements.txt                # Dependências Python
├── .env                           # Configurações (criar manualmente)
├── .gitignore                     # Arquivos ignorados pelo Git
├── README.md                      # Este arquivo
│
├── src/                           # Código core da aplicação
│   ├── __init__.py
│   ├── agent.py                   # Agente principal (LangGraph)
│   ├── guardrails.py              # Sistema de moderação
│   ├── metrics.py                 # Sistema de coleta de métricas
│   └── config.py                  # Configurações centralizadas
│
├── scripts/                       # Scripts utilitários
│   ├── setup_data.py              # Gerador de dados sintéticos
│   ├── setup_vectorstore.py       # Popula o ChromaDB
│   ├── test_metrics.py            # Script para coletar métricas
│   └── generate_visualizations.py # Gerador de gráficos
│
├── data/                          # Dados e documentos
│   ├── credit_risk.db             # Banco SQLite (gerado)
│   ├── chroma_db/                 # Vector store (gerado)
│   └── policies/                  # Políticas e glossário
│       ├── politica_risco.md
│       └── glossario.md
│
└── outputs/                       # Resultados e métricas
    ├── metrics_data.json          # Dados brutos (gerado)
    ├── metrics_export.json        # Dados formatados (gerado)
    ├── metrics_dashboard.png      # Dashboard (gerado)
    └── project_results_linkedin.png # Card redes sociais (gerado)
```

---

## Tecnologias Utilizadas

- **LangChain 0.3+**: Framework para aplicações com LLM
- **LangGraph**: Orquestração de agentes e fluxos complexos
- **OpenAI GPT-4o-mini**: Modelo de linguagem principal
- **ChromaDB 1.5+**: Vector database para RAG
- **Streamlit 1.50+**: Interface web interativa
- **SQLite**: Banco de dados relacional embutido
- **Sentence Transformers**: Embeddings locais (all-MiniLM-L6-v2)
- **Faker**: Geração de dados sintéticos realistas
- **Python-dotenv**: Gerenciamento de variáveis de ambiente

---

## Troubleshooting

### Erro: "No module named 'langchain_chroma'"

**Solução:**
```bash
pip install langchain-chroma
```

### Erro: "OPENAI_API_KEY not found"

**Solução:**
1. Crie um arquivo `.env` na raiz do projeto
2. Adicione: `OPENAI_API_KEY=sua-chave-aqui`
3. Obtenha sua chave em: https://platform.openai.com/api-keys

### Erro: "No such file 'credit_risk.db'"

**Solução:**
```bash
cd scripts
python setup_data.py
cd ..
```

### Erro: "ChromaDB collection not found"

**Solução:**
```bash
cd scripts
python setup_vectorstore.py
cd ..
```

### Performance lenta nas primeiras consultas

**Explicação:** Na primeira execução, o ChromaDB precisa carregar os embeddings. Consultas subsequentes serão mais rápidas.

### Guardrails bloqueando perguntas legítimas

**Explicação:** Se perguntas válidas sobre dados estão sendo bloqueadas, ajuste o system prompt em `src/guardrails.py`.

---

## Regenerando os Dados

Para resetar o banco de dados ou atualizar as políticas:

```bash
cd scripts
python setup_data.py           # Gera novo banco SQLite
python setup_vectorstore.py    # Atualiza ChromaDB
cd ..
```

---

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir melhorias
- Enviar pull requests
- Compartilhar casos de uso

---

## Licença

Este projeto é open source e está disponível sob a licença MIT.

---

## Autor

**Paulo Siqueira**
- GitHub: [@Pasique](https://github.com/Pasique)
- LinkedIn: [Paulo Siqueira](https://www.linkedin.com/in/paulo-henrique-siqueira/)

---

**FinSight AI** - Transformando dados em decisões inteligentes
