"""Geração de posts de LinkedIn e extração de conhecimento via OpenAI."""

from __future__ import annotations

from datetime import date
from typing import List, Optional
from config import LLM_MODEL, LLM_TEMPERATURE, PERSONAS


def build_generation_prompt(
    scraped_articles: List[dict],
    text_snippets: str,
    image_descriptions: str,
    my_thoughts: Optional[str],
    persona_context: str,
    persona_key: str,
) -> List[dict]:
    """Monta a lista de mensagens para a chamada OpenAI."""
    persona_label = PERSONAS[persona_key]["label"]

    system_prompt = f"""Você é um assistente especializado em criar posts de LinkedIn com qualidade editorial real.

Sua tarefa é transformar o conteúdo fornecido em um post autoral — não um resumo.

{persona_context}

=== DIRETRIZES GERAIS ===
- Escreva em português brasileiro
- O post deve refletir a persona acima: tom, público-alvo e temas prioritários
- NÃO comece com "Eu" nem com "Hoje eu aprendi"
- A primeira linha DEVE ser um gancho forte — único elemento visível antes do "Ver mais"
- Parágrafos curtos (1–3 linhas), com linha em branco entre eles
- Máximo 3 hashtags, no final, separadas por linha em branco
- Máximo 2 emojis, usados apenas em pontos estratégicos
- O post deve ter perspectiva própria, insight além da fonte, e ser assinável com orgulho
- Data de hoje: {date.today().isoformat()}
"""

    user_parts = []

    if scraped_articles:
        articles_text = []
        for i, art in enumerate(scraped_articles, 1):
            if art["success"] and art["text"]:
                articles_text.append(
                    f"[Artigo {i}] {art['title']}\nURL: {art['url']}\n\n{art['text']}"
                )
        if articles_text:
            user_parts.append("=== ARTIGOS COLETADOS ===\n" + "\n\n---\n\n".join(articles_text))

    if text_snippets and text_snippets.strip():
        user_parts.append(f"=== TEXTO COLADO / TRECHOS ===\n{text_snippets.strip()}")

    if image_descriptions and image_descriptions.strip():
        user_parts.append(f"=== CONTEÚDO DAS IMAGENS ===\n{image_descriptions.strip()}")

    if my_thoughts and my_thoughts.strip():
        user_parts.append(
            f"=== MEU PENSAMENTO E ÂNGULO EDITORIAL ===\n"
            f"{my_thoughts.strip()}\n\n"
            f"Use esse direcionamento para definir o ângulo e o ponto de vista do post."
        )
    else:
        user_parts.append(
            "=== ÂNGULO EDITORIAL ===\n"
            "Escolha você mesmo o ângulo mais interessante e relevante para a persona, "
            "baseado no conteúdo fornecido."
        )

    user_parts.append(
        f"=== INSTRUÇÃO FINAL ===\n"
        f"Gere agora um post completo para LinkedIn, pronto para publicação, "
        f"seguindo todas as diretrizes da persona '{persona_label}' e das boas práticas acima. "
        f"Retorne APENAS o texto do post — sem título, sem comentários, sem explicações extras."
    )

    user_message = "\n\n".join(user_parts)

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]


def generate_post(
    messages: List[dict],
    model: str,
    temperature: float,
    openai_client,
) -> str:
    """Chama a OpenAI e retorna o texto do post gerado."""
    response = openai_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=800,
    )
    return response.choices[0].message.content.strip()


def extract_knowledge(
    scraped_articles: List[dict],
    text_snippets: str,
    persona_key: str,
    openai_client,
    image_descriptions: str = "",
) -> str:
    """
    Chamada LLM separada e mais barata para extrair conhecimento estruturado da sessão.
    O resultado é salvo como segundo cérebro no vault.
    """
    persona_label = PERSONAS[persona_key]["label"]
    today = date.today().isoformat()

    content_parts = []
    sources_list = []

    for art in scraped_articles:
        if art["success"] and art["text"]:
            content_parts.append(f"Fonte: {art['title']}\n{art['text'][:3000]}")
            sources_list.append(art["url"])

    if text_snippets and text_snippets.strip():
        content_parts.append(f"Texto colado:\n{text_snippets.strip()[:2000]}")

    if image_descriptions and image_descriptions.strip():
        content_parts.append(f"Conteúdo de imagens analisadas:\n{image_descriptions.strip()[:2000]}")

    if not content_parts:
        return ""

    sources_yaml = "\n".join(f"  - {s}" for s in sources_list) if sources_list else "  - (texto colado)"

    prompt = f"""Você é um extrator de conhecimento para um profissional da área de {persona_label}.

Analise o conteúdo abaixo e extraia os 3–5 aprendizados mais relevantes e específicos para um profissional da área.

Formato obrigatório da resposta (markdown):

---
id: {today.replace('-', '')}
persona: {persona_key}
created: {today}
sources:
{sources_yaml}
tags: []
---

# Conhecimento Extraído — {today}

## Tema central
[Uma frase descrevendo o tema principal]

## Aprendizados principais

1. **[Título do aprendizado]** — [Explicação específica com dados/números quando disponível]

2. **[Título do aprendizado]** — [Explicação específica]

3. **[Título do aprendizado]** — [Explicação específica]

## Implicações para a área de {persona_label}
[2–3 frases sobre como isso se aplica na prática para um {persona_label}]

## Fontes processadas nesta sessão
{chr(10).join(f'- {s}' for s in sources_list) if sources_list else '- (texto colado pelo usuário)'}

---

Conteúdo a analisar:

{'---'.join(content_parts)}
"""

    response = openai_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=1000,
    )
    return response.choices[0].message.content.strip()
