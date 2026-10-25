"""Módulo de sanitización para ingesta de noticias pre-partido.

Cumple con el Artículo VI de la Constitución:
El contenido ingerido automáticamente es dato no confiable. Se aplica sanitización
básica para mitigar prompt injections (límite de longitud, remoción de patrones de
instrucción y eliminación de etiquetas de sistema o scripts).
"""

import re

# Patrones conocidos de inyección de instrucciones en español e inglés
INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?(previous|prior)\s+(instructions|prompts)",
    r"(?i)ignora\s+(todas\s+las\s+)?instrucciones\s+(anteriores|previas)",
    r"(?i)disregard\s+(all\s+)?(previous|prior)\s+(instructions|prompts)",
    r"(?i)system\s*:\s*",
    r"(?i)assistant\s*:\s*",
    r"(?i)user\s*:\s*",
    r"(?i)output\s+hacked",
    r"(?i)olvida\s+las\s+instrucciones",
]

# Etiquetas XML/HTML peligrosas que podrían interferir con el delimitado del prompt
DANGEROUS_TAGS = [
    r"(?i)</?system>",
    r"(?i)</?prompt>",
    r"(?i)<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>",
    r"(?i)</?script>",
    r"(?i)<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>",
    r"(?i)</?style>",
]


def sanitize_article_text(text: str, max_length: int = 10000) -> str:
    """Sanitiza el texto de un artículo para evitar inyecciones de prompt.

    Args:
        text: Texto crudo extraído de News API o RSS.
        max_length: Límite máximo de caracteres permitido.

    Returns:
        Texto sanitizado seguro para indexación y uso en contexto RAG.
    """
    if not text:
        return ""

    # 1. Truncar longitud excesiva (evitar ataques DoS / saturación de ventana)
    sanitized = text[:max_length]

    # 2. Remover etiquetas peligrosas
    for tag_pattern in DANGEROUS_TAGS:
        sanitized = re.sub(tag_pattern, "", sanitized)

    # 3. Remover patrones evidentes de inyección de instrucciones
    for pattern in INJECTION_PATTERNS:
        sanitized = re.sub(pattern, "", sanitized)

    # 4. Normalizar espacios en blanco repetidos
    sanitized = re.sub(r"[ \t]+", " ", sanitized)
    sanitized = re.sub(r"\n\s*\n+", "\n\n", sanitized)

    return sanitized.strip()
