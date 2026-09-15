"""
Módulo de chunkeo de noticias pre-partido para el pipeline de RAG.

Cumple con la sección 7.1 del spec y la tarea T010:
- Chunkeo por artículo completo si no excede ~500 tokens.
- Si excede ~500 tokens, aplica solapamiento de 15-20% entre sub-chunks.
"""

from typing import Any, Dict, List, Optional
import math
import re


def estimate_tokens(text: str) -> int:
    """
    Estima el número de tokens de un texto en español/inglés.
    Aproximación estándar: ~4 caracteres por token o ~0.75 palabras por token.
    """
    if not text:
        return 0
    # Contamos palabras y caracteres para una estimación más precisa
    words = len(text.split())
    chars = len(text)
    # Promedio entre palabras * 1.3 y caracteres / 4
    return math.ceil((words * 1.3 + chars / 4) / 2)


def chunk_article(
    text: str,
    title: Optional[str] = None,
    max_tokens: int = 500,
    overlap_ratio: float = 0.15,
) -> List[Dict[str, Any]]:
    """
    Divide un artículo de noticias en chunks respetando la restricción de tokens y solapamiento.

    Args:
        text: Contenido del artículo.
        title: Título opcional de la noticia para añadir como contexto a cada chunk.
        max_tokens: Límite aproximado de tokens por chunk (default 500).
        overlap_ratio: Porcentaje de solapamiento entre chunks continuos (default 0.15 = 15%).

    Returns:
        Lista de diccionarios con información del chunk:
        [
            {
                "chunk_index": 0,
                "total_chunks": N,
                "content": str,
                "token_count": int,
                "title": str
            }, ...
        ]
    """
    cleaned_text = text.strip()
    if not cleaned_text:
        return []

    # Si se incluye título, considerar sus tokens dentro del conteo de contexto
    title_prefix = f"Título: {title.strip()}\n\n" if title and title.strip() else ""
    full_text_with_title = f"{title_prefix}{cleaned_text}"
    total_tokens = estimate_tokens(full_text_with_title)

    # Si la noticia completa cabe dentro de max_tokens, no dividir (sección 7.1 del spec)
    if total_tokens <= max_tokens:
        return [
            {
                "chunk_index": 0,
                "total_chunks": 1,
                "content": full_text_with_title,
                "token_count": total_tokens,
                "title": title or "",
            }
        ]

    # Dividir el contenido en párrafos o oraciones para evitar cortar frases por la mitad
    paragraphs = [p.strip() for p in cleaned_text.split("\n") if p.strip()]
    if not paragraphs:
        paragraphs = [cleaned_text]

    # Calcular tokens deseados por chunk y solapamiento
    content_max_tokens = max_tokens - estimate_tokens(title_prefix)
    overlap_tokens = math.ceil(content_max_tokens * overlap_ratio)

    chunks: List[str] = []
    current_chunk_paragraphs: List[str] = []
    current_tokens = 0

    for paragraph in paragraphs:
        p_tokens = estimate_tokens(paragraph)

        # Si un solo párrafo es excesivamente largo, lo dividimos por oraciones
        if p_tokens > content_max_tokens:
            sentences = re.split(r"(?<=[.!?])\s+", paragraph)
            for sentence in sentences:
                s_tokens = estimate_tokens(sentence)
                if current_tokens + s_tokens > content_max_tokens and current_chunk_paragraphs:
                    chunks.append("\n".join(current_chunk_paragraphs))
                    # Retener oraciones finales para cumplir con el overlap_ratio
                    current_chunk_paragraphs = _get_overlap_paragraphs(
                        current_chunk_paragraphs, overlap_tokens
                    )
                    current_tokens = sum(estimate_tokens(p) for p in current_chunk_paragraphs)

                current_chunk_paragraphs.append(sentence)
                current_tokens += s_tokens
        else:
            if current_tokens + p_tokens > content_max_tokens and current_chunk_paragraphs:
                chunks.append("\n".join(current_chunk_paragraphs))
                # Retener contenido previo para overlap
                current_chunk_paragraphs = _get_overlap_paragraphs(
                    current_chunk_paragraphs, overlap_tokens
                )
                current_tokens = sum(estimate_tokens(p) for p in current_chunk_paragraphs)

            current_chunk_paragraphs.append(paragraph)
            current_tokens += p_tokens

    if current_chunk_paragraphs:
        chunks.append("\n".join(current_chunk_paragraphs))

    total_chunks = len(chunks)
    result = []
    for idx, chunk_text in enumerate(chunks):
        formatted_content = f"{title_prefix}{chunk_text}"
        result.append(
            {
                "chunk_index": idx,
                "total_chunks": total_chunks,
                "content": formatted_content,
                "token_count": estimate_tokens(formatted_content),
                "title": title or "",
            }
        )

    return result


def _get_overlap_paragraphs(paragraphs: List[str], overlap_tokens: int) -> List[str]:
    """Retorna los últimos párrafos que acumulan hasta overlap_tokens para mantener contexto."""
    overlap: List[str] = []
    accumulated = 0
    for p in reversed(paragraphs):
        p_tokens = estimate_tokens(p)
        if accumulated + p_tokens > overlap_tokens and overlap:
            break
        overlap.insert(0, p)
        accumulated += p_tokens
    return overlap
