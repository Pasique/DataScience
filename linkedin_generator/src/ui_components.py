"""CSS customizado e componentes auxiliares para o Streamlit."""

from __future__ import annotations

import json
from typing import List
import streamlit as st
import streamlit.components.v1 as components

CUSTOM_CSS = """
<style>
/* ── Layout geral ─────────────────────────────────────────────────── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* ── Tipografia ───────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* ── Header da aplicação ──────────────────────────────────────────── */
.app-header {
    background: linear-gradient(135deg, #0a66c2 0%, #004182 100%);
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    color: white;
}

.app-header h1 {
    color: white !important;
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0;
    padding: 0;
}

.app-header p {
    color: rgba(255,255,255,0.8);
    margin: 0.3rem 0 0 0;
    font-size: 0.95rem;
}

/* ── Cards de seção ───────────────────────────────────────────────── */
.section-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    border: 1px solid #e8ecf0;
    margin-bottom: 1rem;
}

.section-title {
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #6b7280;
    margin-bottom: 0.75rem;
}

/* ── Post gerado ──────────────────────────────────────────────────── */
.post-card {
    background: #f8fafc;
    border-left: 4px solid #0a66c2;
    border-radius: 0 12px 12px 0;
    padding: 1.5rem 1.75rem;
    font-size: 0.95rem;
    line-height: 1.75;
    white-space: pre-wrap;
    min-height: 280px;
    color: #1a1a2e;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.post-placeholder {
    background: #f8fafc;
    border: 2px dashed #d1d5db;
    border-radius: 12px;
    padding: 3rem 2rem;
    text-align: center;
    color: #9ca3af;
    min-height: 280px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 0.5rem;
}

/* ── Status de URL ────────────────────────────────────────────────── */
.url-result {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    padding: 0.5rem 0.75rem;
    border-radius: 8px;
    margin-bottom: 0.4rem;
    font-size: 0.85rem;
}

.url-success {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    color: #15803d;
}

.url-error {
    background: #fef2f2;
    border: 1px solid #fecaca;
    color: #b91c1c;
}

.url-icon { font-size: 1rem; flex-shrink: 0; }
.url-title { font-weight: 600; }
.url-domain { color: inherit; opacity: 0.7; font-size: 0.78rem; }

/* ── Seletor de persona ───────────────────────────────────────────── */
.persona-card {
    border: 2px solid #e5e7eb;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    cursor: pointer;
    transition: all 0.2s;
    text-align: center;
}

.persona-card.active {
    border-color: #0a66c2;
    background: #eff6ff;
}

/* ── Botão primário ───────────────────────────────────────────────── */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0a66c2 0%, #004182 100%);
    color: white;
    border: none;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.95rem;
    padding: 0.6rem 1.5rem;
    width: 100%;
    transition: opacity 0.2s;
}

div.stButton > button[kind="primary"]:hover {
    opacity: 0.9;
}

/* ── Botão secundário ─────────────────────────────────────────────── */
div.stButton > button[kind="secondary"] {
    border-radius: 20px;
    font-weight: 500;
}

/* ── Salvo com sucesso ────────────────────────────────────────────── */
.save-success {
    background: #f0fdf4;
    border: 1px solid #86efac;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    color: #15803d;
    font-size: 0.87rem;
    margin-top: 0.75rem;
}

/* ── Fontes usadas no painel direito ──────────────────────────────── */
.source-chip {
    display: inline-block;
    background: #eff6ff;
    color: #1d4ed8;
    border-radius: 20px;
    padding: 0.2rem 0.75rem;
    font-size: 0.78rem;
    margin: 0.2rem 0.15rem;
    font-weight: 500;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* ── Divider customizado ──────────────────────────────────────────── */
.custom-divider {
    height: 1px;
    background: #e5e7eb;
    margin: 1rem 0;
}

/* ── Loading overlay ──────────────────────────────────────────────── */
@keyframes loading-pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.45; }
}

.loading-overlay {
    text-align: center;
    padding: 1.5rem 2rem;
    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    border-radius: 12px;
    border: 1px solid #93c5fd;
    margin: 0.5rem 0;
    animation: loading-pulse 1.8s ease-in-out infinite;
}

.loading-overlay .loading-msg {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1d4ed8;
    margin-bottom: 0.3rem;
}

.loading-overlay .loading-sub {
    font-size: 0.85rem;
    color: #6b7280;
}
</style>
"""


def inject_css() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_url_status(articles: List[dict]) -> None:
    """Renderiza o status de cada URL processada."""
    if not articles:
        return
    for art in articles:
        if art["success"]:
            domain = art["url"].split("/")[2] if "/" in art["url"] else art["url"]
            title = art["title"] or domain
            st.markdown(
                f'<div class="url-result url-success">'
                f'<span class="url-icon">✓</span>'
                f'<div><div class="url-title">{title[:55]}{"…" if len(title) > 55 else ""}</div>'
                f'<div class="url-domain">{domain}</div></div>'
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            domain = art["url"][:40]
            st.markdown(
                f'<div class="url-result url-error">'
                f'<span class="url-icon">✗</span>'
                f'<div><div class="url-title">Falha ao acessar</div>'
                f'<div class="url-domain">{domain}</div></div>'
                f"</div>",
                unsafe_allow_html=True,
            )


def render_post_output(post_text: str) -> None:
    """Renderiza o post gerado no card estilizado."""
    st.markdown(
        f'<div class="post-card">{post_text}</div>',
        unsafe_allow_html=True,
    )


def render_post_placeholder() -> None:
    """Renderiza o placeholder quando nenhum post foi gerado ainda."""
    st.markdown(
        '<div class="post-placeholder">'
        '<div style="font-size:2rem">✍️</div>'
        '<div style="font-weight:600;color:#6b7280">O post aparecerá aqui</div>'
        '<div style="font-size:0.85rem">Adicione fontes e clique em Gerar Post</div>'
        "</div>",
        unsafe_allow_html=True,
    )


def render_source_chips(articles: List[dict], has_text: bool, has_images: bool) -> None:
    """Renderiza chips compactos das fontes usadas na geração."""
    chips = []
    for art in articles:
        if art["success"]:
            domain = art["url"].split("/")[2] if "/" in art["url"] else art["url"]
            chips.append(f'<span class="source-chip">🔗 {domain}</span>')
    if has_text:
        chips.append('<span class="source-chip">📝 Texto colado</span>')
    if has_images:
        chips.append('<span class="source-chip">🖼️ Imagens</span>')
    if chips:
        st.markdown("**Fontes usadas:**", unsafe_allow_html=False)
        st.markdown("".join(chips), unsafe_allow_html=True)


def render_copy_button(post_text: str) -> None:
    """Botão de copiar texto para área de transferência."""
    # json.dumps garante escape correto de aspas, quebras de linha etc.
    # O texto é atribuído via <script> para não quebrar atributos HTML.
    escaped = json.dumps(post_text)
    components.html(
        f"""
        <script>
        var _postText = {escaped};
        function doCopy() {{
            var el = document.createElement('textarea');
            el.value = _postText;
            el.setAttribute('readonly', '');
            el.style.cssText = 'position:fixed;top:-9999px;left:-9999px';
            document.body.appendChild(el);
            el.select();
            var ok = document.execCommand('copy');
            document.body.removeChild(el);
            if (!ok && navigator.clipboard) {{
                navigator.clipboard.writeText(_postText).catch(function(){{}});
            }}
            var b = document.getElementById('cpbtn');
            b.innerHTML = ok ? '&#10003; Copiado!' : '&#128203; Copiar texto';
            if (ok) b.style.background = 'linear-gradient(135deg,#15803d,#166534)';
            setTimeout(function() {{
                b.innerHTML = '&#128203; Copiar texto';
                b.style.background = 'linear-gradient(135deg,#0a66c2,#004182)';
            }}, 2000);
        }}
        </script>
        <button id="cpbtn" onclick="doCopy()"
            style="background:linear-gradient(135deg,#0a66c2,#004182);color:white;border:none;
                   border-radius:20px;font-weight:600;font-size:0.9rem;padding:0.5rem 1.1rem;
                   cursor:pointer;width:100%;transition:all 0.2s;
                   font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif"
        >&#128203; Copiar texto</button>
        """,
        height=42,
    )


def render_loading(placeholder, message: str) -> None:
    """Exibe indicador de carregamento animado no placeholder full-width."""
    placeholder.markdown(
        f'<div class="loading-overlay">'
        f'<div class="loading-msg">{message}</div>'
        f'<div class="loading-sub">Aguarde um momento…</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_save_success(path) -> None:
    """Exibe confirmação de salvamento com o caminho do arquivo."""
    st.markdown(
        f'<div class="save-success">💾 Salvo em: <code>{path.name}</code></div>',
        unsafe_allow_html=True,
    )
