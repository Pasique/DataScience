"""Processamento de imagens para a OpenAI Vision API."""

import base64
from io import BytesIO
from config import VISION_MODEL


def encode_image_to_base64(uploaded_file) -> str:
    """Converte um UploadedFile do Streamlit para string base64."""
    uploaded_file.seek(0)
    data = uploaded_file.read()
    return base64.b64encode(data).decode("utf-8")


def _get_mime_type(filename: str) -> str:
    ext = filename.lower().rsplit(".", 1)[-1]
    return {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "gif": "image/gif", "webp": "image/webp"}.get(ext, "image/jpeg")


def extract_text_from_images(uploaded_files: list, openai_client) -> str:
    """
    Envia imagens para o GPT-4o Vision e retorna descrição textual consolidada.
    Chamada única por sessão — resultado armazenado em session_state pelo app.
    """
    if not uploaded_files:
        return ""

    content = [
        {
            "type": "text",
            "text": (
                "Analise cada imagem abaixo. Para cada uma:\n"
                "1. Descreva o que está sendo mostrado (gráfico, texto, interface, etc.)\n"
                "2. Extraia todo texto legível\n"
                "3. Identifique dados, métricas ou insights relevantes\n"
                "4. Indique o tema central da imagem\n\n"
                "Seja específico e inclua todos os números e textos visíveis. "
                "Responda em português."
            ),
        }
    ]

    for f in uploaded_files:
        b64 = encode_image_to_base64(f)
        mime = _get_mime_type(f.name)
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}", "detail": "high"},
            }
        )

    response = openai_client.chat.completions.create(
        model=VISION_MODEL,
        messages=[{"role": "user", "content": content}],
        max_tokens=1500,
    )
    return response.choices[0].message.content.strip()
