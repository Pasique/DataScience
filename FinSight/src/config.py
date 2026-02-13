"""Configurações centralizadas do FinSight."""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"

# Database
DB_PATH = f"sqlite:///{DATA_DIR}/credit_risk.db"

# ChromaDB
CHROMA_PATH = str(DATA_DIR / "chroma_db")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# LLM
LLM_MODEL = "gpt-4o-mini"
LLM_TEMPERATURE = 0

# Métricas
METRICS_FILE = str(OUTPUTS_DIR / "metrics_data.json")

# Custos estimados (por milhão de tokens)
COST_INPUT_PER_M = 0.15   # USD
COST_OUTPUT_PER_M = 0.60  # USD
COST_AVG_PER_M = 0.375    # Média 50/50

# Guardrails
GUARDRAIL_TOKENS_ESTIMATE = 50
BLOCKED_QUERY_TOKENS_SAVED = 1500

# RAG
RAG_TOP_K = 3

# Criar diretórios necessários
DATA_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)
