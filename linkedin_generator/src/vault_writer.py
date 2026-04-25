"""Gravação de posts gerados no vault Obsidian com frontmatter YAML."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List
from slugify import slugify
from config import POSTS_DIR, PERSONAS


def save_post_to_vault(
    post_text: str,
    persona_key: str,
    sources: List[str],
    title: str = "",
) -> Path:
    """
    Salva o post gerado como .md no vault.
    Filename: YYYYMMDD_HHMM_{persona}_{slug}.md
    """
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    persona_posts_dir = POSTS_DIR / persona_key
    persona_posts_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    persona_label = PERSONAS[persona_key]["label"]

    if not title:
        first_line = post_text.strip().split("\n")[0]
        title = first_line[:60].rstrip(".")

    slug = slugify(title, max_length=40, separator="_") or "post"
    filename = f"{now.strftime('%Y%m%d_%H%M')}_{slug}.md"
    path = persona_posts_dir / filename

    frontmatter = _build_frontmatter(
        title=title,
        persona_key=persona_key,
        persona_label=persona_label,
        sources=sources,
        created=now.strftime("%Y-%m-%d"),
    )

    footer = (
        f"\n\n---\n"
        f"*Post gerado com LinkedIn Generator em {now.strftime('%Y-%m-%d %H:%M')}*\n"
        f"*Persona: {persona_label}*"
    )

    content = f"{frontmatter}\n\n{post_text}{footer}"
    path.write_text(content, encoding="utf-8")
    return path


def _build_frontmatter(
    title: str,
    persona_key: str,
    persona_label: str,
    sources: List[str],
    created: str,
) -> str:
    sources_yaml = "\n".join(f"  - {s}" for s in sources) if sources else "  []"
    return (
        f"---\n"
        f"title: \"{title}\"\n"
        f"persona: {persona_key}\n"
        f"persona_label: {persona_label}\n"
        f"created: {created}\n"
        f"status: rascunho\n"
        f"tags: [linkedin, post, {persona_key}]\n"
        f"sources:\n{sources_yaml}\n"
        f"---"
    )
