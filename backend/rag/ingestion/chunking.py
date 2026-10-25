"""Módulo de chunking para ingesta de noticias pre-partido.

Cumple con la sección 7.1 de project_spec.md y RF-001:
Chunkeo por artículo completo como unidad preferida. Si un artículo
excede ~500 tokens, se aplica un overlap de 15-20% entre sub-chunks.
"""

import math
import re


def estimate_tokens(text: str) -> int:
    """Estimación conservadora de tokens para español (1 token ~ 0.75 palabras o 4 caracteres)."""
    words = len(text.split())
    return max(1, math.ceil(words * 1.3))


def chunk_article(
    text: str,
    max_tokens: int = 500,
    overlap_pct: float = 0.20,
) -> list[str]:
    """Divide un artículo en chunks preservando el contexto.

    Args:
        text: Texto del artículo a chunkear.
        max_tokens: Límite aproximado de tokens por chunk (~500 por defecto).
        overlap_pct: Porcentaje de overlap entre chunks consecutivos (15-20%).

    Returns:
        Lista de fragmentos de texto (chunks).
    """
    clean_text = text.strip()
    if not clean_text:
        return []

    tokens = estimate_tokens(clean_text)
    if tokens <= max_tokens:
        return [clean_text]

    # Si excede el límite, dividimos por oraciones o palabras
    sentences = re.split(r"(?<=[.!?])\s+", clean_text)
    chunks: list[str] = []
    current_chunk_sentences: list[str] = []
    current_tokens = 0

    for sentence in sentences:
        s_tokens = estimate_tokens(sentence)
        if current_tokens + s_tokens > max_tokens and current_chunk_sentences:
            chunk_str = " ".join(current_chunk_sentences).strip()
            chunks.append(chunk_str)

            # Calcular oraciones para el overlap
            overlap_target = int(max_tokens * overlap_pct)
            overlap_sentences: list[str] = []
            overlap_tokens = 0
            for prev_s in reversed(current_chunk_sentences):
                p_tokens = estimate_tokens(prev_s)
                if overlap_tokens + p_tokens <= overlap_target or not overlap_sentences:
                    overlap_sentences.insert(0, prev_s)
                    overlap_tokens += p_tokens
                else:
                    break

            current_chunk_sentences = [*overlap_sentences, sentence]
            current_tokens = overlap_tokens + s_tokens
        else:
            current_chunk_sentences.append(sentence)
            current_tokens += s_tokens

    if current_chunk_sentences:
        remaining_chunk = " ".join(current_chunk_sentences).strip()
        if not chunks or remaining_chunk != chunks[-1]:
            chunks.append(remaining_chunk)

    return chunks
