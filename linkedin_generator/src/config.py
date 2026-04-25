"""Configurações centralizadas do LinkedIn Post Generator."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths do projeto ────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent

# ── Paths do vault Obsidian ─────────────────────────────────────────────────
VAULT_ROOT = Path("/Users/phsiqueira/Documents/padrao/10_Atlas/13_Projetos/LinkedIn_Generator")
PERSONAS_DIR = VAULT_ROOT / "personas"
POSTS_DIR = VAULT_ROOT / "posts"
CONHECIMENTO_DIR = VAULT_ROOT / "conhecimento"
BOAS_PRATICAS_FILE = VAULT_ROOT / "boas_praticas_posts.md"

# ── Personas ────────────────────────────────────────────────────────────────
PERSONAS = {
    "gerente_financeiro": {
        "label": "Gerente Financeiro",
        "emoji": "💼",
        "file": PERSONAS_DIR / "gerente_financeiro.md",
        "conhecimento_dir": CONHECIMENTO_DIR / "gerente_financeiro",
    },
    "cientista_dados": {
        "label": "Cientista de Dados / ML / IA",
        "emoji": "🤖",
        "file": PERSONAS_DIR / "cientista_dados.md",
        "conhecimento_dir": CONHECIMENTO_DIR / "cientista_dados",
    },
}

# ── OpenAI ──────────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = "gpt-4o-mini"        # Geração de post e extração de conhecimento
VISION_MODEL = "gpt-4o"          # Análise de imagens (Vision API)
LLM_TEMPERATURE = 0.75

# ── Scraping ────────────────────────────────────────────────────────────────
SCRAPE_TIMEOUT = 15              # segundos por URL
MAX_TEXT_PER_URL = 6000          # caracteres máximos por artigo scrapeado

# ── Segundo cérebro ─────────────────────────────────────────────────────────
MAX_KNOWLEDGE_FILES = 5          # arquivos mais recentes injetados no prompt


def ensure_vault_dirs() -> None:
    """Garante que todas as pastas do vault existam. Chamada no startup do app."""
    for path in [PERSONAS_DIR, POSTS_DIR]:
        path.mkdir(parents=True, exist_ok=True)
    for key, persona_cfg in PERSONAS.items():
        persona_cfg["conhecimento_dir"].mkdir(parents=True, exist_ok=True)
        (POSTS_DIR / key).mkdir(parents=True, exist_ok=True)
