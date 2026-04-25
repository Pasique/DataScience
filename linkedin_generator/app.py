"""LinkedIn Post Generator — Aplicação principal Streamlit."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import streamlit as st
from openai import OpenAI

from config import (
    ensure_vault_dirs,
    PERSONAS,
    LLM_MODEL,
    LLM_TEMPERATURE,
    OPENAI_API_KEY,
)
from scraper import scrape_urls
from image_handler import extract_text_from_images
from post_generator import build_generation_prompt, generate_post, extract_knowledge
from knowledge_manager import build_context_block, save_knowledge
from vault_writer import save_post_to_vault
from ui_components import (
    inject_css,
    render_url_status,
    render_post_output,
    render_post_placeholder,
    render_source_chips,
    render_save_success,
    render_loading,
    render_copy_button,
)

# ── Inicialização ────────────────────────────────────────────────────────────
ensure_vault_dirs()

st.set_page_config(
    page_title="LinkedIn Post Generator",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_css()

# OpenAI client
if not OPENAI_API_KEY:
    st.error("⚠️ OPENAI_API_KEY não encontrada. Crie o arquivo .env com sua chave.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# ── Session state ────────────────────────────────────────────────────────────
_defaults = {
    "url_count": 1,
    "upload_key": 0,
    "scraped_articles": [],
    "image_descriptions": "",
    "generated_post": "",
    "saved_path": None,
    "knowledge_saved": False,
    "last_urls": [],
    "last_persona": None,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Header ───────────────────────────────────────────────────────────────────
header_col, clear_col = st.columns([0.85, 0.15])
with header_col:
    st.markdown(
        '<div class="app-header">'
        "<h1>🔗 LinkedIn Post Generator</h1>"
        "<p>Gere posts autorais com base em artigos, textos e imagens — com memória por persona.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
with clear_col:
    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
    if st.button("🗑️ Limpar tudo", key="btn_clear"):
        new_upload_key = st.session_state.get("upload_key", 0) + 1
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.session_state["upload_key"] = new_upload_key
        st.rerun()

# ── Seletor de Persona ───────────────────────────────────────────────────────
persona_cols = st.columns(len(PERSONAS))
persona_keys = list(PERSONAS.keys())

if "persona_key" not in st.session_state:
    st.session_state["persona_key"] = persona_keys[0]

for i, (key, cfg) in enumerate(PERSONAS.items()):
    with persona_cols[i]:
        is_active = st.session_state["persona_key"] == key
        border_color = "#0a66c2" if is_active else "#e5e7eb"
        bg_color = "#eff6ff" if is_active else "#ffffff"
        st.markdown(
            f'<div style="border:2px solid {border_color};border-radius:12px;'
            f'padding:1rem 1.25rem;background:{bg_color};text-align:center;margin-bottom:0.5rem;">'
            f'<div style="font-size:1.8rem;color:#1a1a2e;line-height:1.2">{cfg["emoji"]}</div>'
            f'<div style="font-weight:700;color:#1a1a2e;font-size:0.95rem;margin-top:0.3rem">{cfg["label"]}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
        if st.button(
            "Selecionar" if not is_active else "✓ Selecionado",
            key=f"btn_persona_{key}",
            type="primary" if is_active else "secondary",
        ):
            st.session_state["persona_key"] = key
            st.session_state["generated_post"] = ""
            st.session_state["saved_path"] = None
            st.rerun()

persona_key = st.session_state["persona_key"]
persona_label = PERSONAS[persona_key]["label"]

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# Placeholder full-width para loading — aparece entre personas e colunas
loading_placeholder = st.empty()

# ── Layout principal: 2 colunas ──────────────────────────────────────────────
col_left, col_right = st.columns([0.44, 0.56], gap="large")

# ════════════════════════════════════════════════════════════════════════════
# COLUNA ESQUERDA — Fontes de entrada
# ════════════════════════════════════════════════════════════════════════════
with col_left:

    # ── URLs ────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🔗 URLs de Artigos</div>', unsafe_allow_html=True)

    urls = []
    for i in range(st.session_state["url_count"]):
        url = st.text_input(
            f"URL {i + 1}",
            key=f"url_{i}",
            placeholder="https://...",
            label_visibility="collapsed" if i > 0 else "visible",
        )
        if url and url.strip():
            urls.append(url.strip())

    add_col, _ = st.columns([1, 2])
    with add_col:
        if st.button("➕ Adicionar URL", key="btn_add_url"):
            st.session_state["url_count"] += 1
            st.rerun()

    # Status dos artigos já scrapeados
    if st.session_state["scraped_articles"]:
        render_url_status(st.session_state["scraped_articles"])

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ── Texto colado ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📝 Texto Colado</div>', unsafe_allow_html=True)
    text_snippet = st.text_area(
        "Texto colado",
        height=130,
        key="text_snippet",
        placeholder="Cole aqui trechos de artigos, resumos, transcrições ou qualquer texto que você leu e quer usar como base...",
        label_visibility="collapsed",
    )

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ── Imagens ───────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🖼️ Imagens / Screenshots</div>', unsafe_allow_html=True)
    uploaded_images = st.file_uploader(
        "Imagens",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
        key=f"uploaded_images_{st.session_state['upload_key']}",
        label_visibility="collapsed",
    )

    if uploaded_images:
        img_col1, img_col2 = st.columns(2)
        with img_col1:
            st.caption(f"{len(uploaded_images)} imagem(ns) carregada(s)")
        with img_col2:
            if st.button("🔍 Processar Imagens", key="btn_process_images"):
                with st.spinner("Analisando com GPT-4o Vision..."):
                    try:
                        st.session_state["image_descriptions"] = extract_text_from_images(
                            uploaded_images, client
                        )
                        st.success("Imagens processadas com sucesso.")
                    except Exception as e:
                        st.error(f"Erro ao processar imagens: {e}")

        if st.session_state["image_descriptions"]:
            with st.expander("Ver descrição das imagens"):
                st.write(st.session_state["image_descriptions"])

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ── Meu pensamento (toggle) ───────────────────────────────────────────────
    st.markdown('<div class="section-title">💭 Meu Pensamento</div>', unsafe_allow_html=True)
    use_my_thoughts = st.toggle(
        "Definir ângulo editorial manualmente",
        value=False,
        key="use_my_thoughts",
        help="Se desativado, o modelo escolhe o ângulo mais interessante por conta própria.",
    )

    my_thoughts = None
    if use_my_thoughts:
        my_thoughts = st.text_area(
            "Meu pensamento",
            height=110,
            key="my_thoughts_text",
            placeholder="O que você pensa sobre o assunto? Qual ângulo ou ponto de vista quer explorar no post?",
            label_visibility="collapsed",
        )

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ── Botão Gerar ───────────────────────────────────────────────────────────
    if st.button("🚀 Gerar Post", type="primary", key="btn_generate"):
        # Auto-process images if uploaded but not yet processed
        if uploaded_images and not st.session_state["image_descriptions"]:
            render_loading(loading_placeholder, "🖼️ Processando imagens com GPT-4o Vision...")
            try:
                st.session_state["image_descriptions"] = extract_text_from_images(
                    uploaded_images, client
                )
            except Exception as e:
                loading_placeholder.empty()
                st.error(f"Erro ao processar imagens: {e}")
                st.stop()

        has_content = bool(urls or (text_snippet and text_snippet.strip()) or st.session_state["image_descriptions"])
        if not has_content:
            st.error("Adicione ao menos uma fonte: URL, texto colado ou imagem.")
        else:
            # Reset estado anterior
            st.session_state["generated_post"] = ""
            st.session_state["saved_path"] = None
            st.session_state["knowledge_saved"] = False

            # Scraping
            if urls:
                render_loading(loading_placeholder, f"🔍 Buscando {len(urls)} artigo(s)...")
                st.session_state["scraped_articles"] = scrape_urls(urls)
                st.session_state["last_urls"] = urls
            else:
                st.session_state["scraped_articles"] = []

            # Geração do post
            render_loading(loading_placeholder, f"✍️ Gerando post como {persona_label}...")
            try:
                context = build_context_block(persona_key)
                messages = build_generation_prompt(
                    scraped_articles=st.session_state["scraped_articles"],
                    text_snippets=text_snippet or "",
                    image_descriptions=st.session_state["image_descriptions"],
                    my_thoughts=my_thoughts,
                    persona_context=context,
                    persona_key=persona_key,
                )
                post = generate_post(messages, LLM_MODEL, LLM_TEMPERATURE, client)
                st.session_state["generated_post"] = post
            except Exception as e:
                loading_placeholder.empty()
                st.error(f"Erro ao gerar post: {e}")
                st.stop()

            st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# COLUNA DIREITA — Post gerado
# ════════════════════════════════════════════════════════════════════════════
with col_right:
    st.markdown(
        f'<div class="section-title">✍️ POST GERADO — {persona_label.upper()}</div>',
        unsafe_allow_html=True,
    )

    if st.session_state["generated_post"]:
        render_post_output(st.session_state["generated_post"])

        st.markdown("")

        action_col1, action_col2, action_col3 = st.columns(3)
        with action_col1:
            if st.button("💾 Salvar no Obsidian", key="btn_save", type="primary"):
                try:
                    path = save_post_to_vault(
                        post_text=st.session_state["generated_post"],
                        persona_key=persona_key,
                        sources=st.session_state.get("last_urls", []),
                    )
                    st.session_state["saved_path"] = path
                    # Extração de conhecimento ao salvar
                    try:
                        knowledge_text = extract_knowledge(
                            scraped_articles=st.session_state["scraped_articles"],
                            text_snippets=st.session_state.get("text_snippet", ""),
                            persona_key=persona_key,
                            openai_client=client,
                            image_descriptions=st.session_state["image_descriptions"],
                        )
                        if knowledge_text:
                            from datetime import date
                            save_knowledge(
                                persona_key=persona_key,
                                title=f"Sessão {date.today().isoformat()}",
                                knowledge_text=knowledge_text,
                            )
                            st.session_state["knowledge_saved"] = True
                    except Exception as e:
                        st.caption(f"⚠️ Conhecimento não salvo: {e}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

        with action_col2:
            render_copy_button(st.session_state["generated_post"])

        with action_col3:
            if st.button("🔄 Nova versão", key="btn_regen"):
                render_loading(loading_placeholder, f"✍️ Gerando nova versão como {persona_label}...")
                try:
                    context = build_context_block(persona_key)
                    messages = build_generation_prompt(
                        scraped_articles=st.session_state["scraped_articles"],
                        text_snippets=st.session_state.get("text_snippet", ""),
                        image_descriptions=st.session_state["image_descriptions"],
                        my_thoughts=my_thoughts,
                        persona_context=context,
                        persona_key=persona_key,
                    )
                    post = generate_post(messages, LLM_MODEL, LLM_TEMPERATURE + 0.1, client)
                    st.session_state["generated_post"] = post
                    st.session_state["saved_path"] = None
                    st.rerun()
                except Exception as e:
                    loading_placeholder.empty()
                    st.error(f"Erro: {e}")

        if st.session_state["saved_path"]:
            render_save_success(st.session_state["saved_path"])

        if st.session_state.get("knowledge_saved"):
            st.caption("🧠 Conhecimento desta sessão salvo no segundo cérebro do Obsidian.")

        # Fontes usadas
        if (
            st.session_state["scraped_articles"]
            or text_snippet
            or st.session_state["image_descriptions"]
        ):
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            render_source_chips(
                articles=st.session_state["scraped_articles"],
                has_text=bool(text_snippet and text_snippet.strip()),
                has_images=bool(st.session_state["image_descriptions"]),
            )

    else:
        render_post_placeholder()

    # Nota informativa sobre o vault
    st.markdown("")
    st.info(
        f"📂 Posts salvos em:\n`…/posts/{persona_key}/`\n\n"
        f"🧠 Segundo cérebro em:\n`…/conhecimento/{persona_key}/`",
        icon=None,
    )
