"""Leitura e escrita de arquivos de conhecimento no vault Obsidian."""

from datetime import datetime
from pathlib import Path
from slugify import slugify
from config import PERSONAS, BOAS_PRATICAS_FILE, MAX_KNOWLEDGE_FILES


def load_persona_md(persona_key: str) -> str:
    """Lê o arquivo de preferências da persona. Retorna string vazia se não existir."""
    path: Path = PERSONAS[persona_key]["file"]
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def load_boas_praticas() -> str:
    """Lê o arquivo de boas práticas do vault."""
    if BOAS_PRATICAS_FILE.exists():
        return BOAS_PRATICAS_FILE.read_text(encoding="utf-8")
    return ""


def load_persona_knowledge(persona_key: str) -> str:
    """
    Lê os arquivos de conhecimento mais recentes da persona (até MAX_KNOWLEDGE_FILES).
    Retorna string concatenada com separadores.
    """
    conhecimento_dir: Path = PERSONAS[persona_key]["conhecimento_dir"]
    files = sorted(conhecimento_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    recent = files[:MAX_KNOWLEDGE_FILES]

    if not recent:
        return ""

    parts = []
    for f in recent:
        content = f.read_text(encoding="utf-8")
        parts.append(f"--- Arquivo: {f.name} ---\n{content}")
    return "\n\n".join(parts)


def save_knowledge(persona_key: str, title: str, knowledge_text: str) -> Path:
    """
    Salva conhecimento extraído da sessão no vault.
    Filename: YYYYMMDD_HHMM_{slug}.md
    """
    conhecimento_dir: Path = PERSONAS[persona_key]["conhecimento_dir"]
    conhecimento_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    slug = slugify(title, max_length=40, separator="_") or "sessao"
    filename = f"{now.strftime('%Y%m%d_%H%M')}_{slug}.md"
    path = conhecimento_dir / filename
    path.write_text(knowledge_text, encoding="utf-8")
    return path


def build_context_block(persona_key: str) -> str:
    """
    Monta o bloco de contexto completo para injeção no prompt de geração.
    Ordem: preferências da persona → boas práticas → conhecimento prévio.
    """
    persona_md = load_persona_md(persona_key)
    boas_praticas = load_boas_praticas()
    prior_knowledge = load_persona_knowledge(persona_key)

    parts = []

    if persona_md:
        parts.append(f"=== PERFIL DA PERSONA ===\n{persona_md}")

    if boas_praticas:
        parts.append(f"=== BOAS PRÁTICAS DE POSTS ===\n{boas_praticas}")

    if prior_knowledge:
        parts.append(
            f"=== CONHECIMENTO PRÉVIO ACUMULADO (último(s) {MAX_KNOWLEDGE_FILES} arquivo(s)) ===\n"
            f"{prior_knowledge}"
        )

    return "\n\n".join(parts)
