"""
Módulo de sanitización de contenido ingerido de fuentes externas (RSS / News API).

Cumple con el Artículo VI de la Constitución de The Playbook y la tarea T011:
- Sanitización anti-prompt-injection para tratar todo contenido ingerido como DATO NO CONFIABLE.
- Recorte por límite de longitud máxima.
- Remoción de patrones de instrucción directa y etiquetas XML no permitidas.
"""

from dataclasses import dataclass
import re


# Patrones comunes de prompt injection a neutralizar (en español e inglés)
PROMPT_INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+|previous\s+|prior\s+)?instructions?",
    r"(?i)ignora\s+(las\s+|todas\s+las\s+)?instrucciones(\s+anteriores)?",
    r"(?i)system\s*prompt\s*:",
    r"(?i)you\s+are\s+now\s+(a|an)?",
    r"(?i)ahora\s+eres\s+(un|una)?",
    r"(?i)forget\s+(everything|above\s+instructions?)",
    r"(?i)olvida\s+(todo|las\s+instrucciones)",
    r"(?i)act\s+as\s+",
    r"(?i)actua\s+como\s+",
    r"(?i)disregard\s+(previous|above)\s+text",
    r"(?i)override\s+(system|developer)\s+instructions?",
]

# Etiquetas XML/HTML reservadas para el formateo de prompts que deben ser escapadas o removidas
RESERVED_XML_TAGS = [
    r"</?context[^>]*>",
    r"</?system[^>]*>",
    r"</?instruction[^>]*>",
    r"</?prompt[^>]*>",
    r"</?noticia[^>]*>",
    r"</?evidencia[^>]*>",
]

# Expresión regular para eliminar scripts y tags HTML indeseados de scraping
HTML_TAG_RE = re.compile(r"<script[^>]*>.*?</script>|<style[^>]*>.*?</style>|<[^>]+>", re.IGNORECASE | re.DOTALL)


@dataclass
class SanitizationResult:
    """Resultado de la sanitización de un texto."""
    sanitized_text: str
    original_length: int
    sanitized_length: int
    was_truncated: bool
    injection_patterns_found: int


def sanitize_text(text: str, max_chars: int = 10000) -> SanitizationResult:
    """
    Sanitiza un texto ingerido de la web antes de indexarlo en el vector database.

    Args:
        text: Contenido plano o HTML ligero proveniente del scraper/API.
        max_chars: Longitud máxima de caracteres permitida (default 10,000).

    Returns:
        SanitizationResult con el texto limpio y metadatos de sanitización.
    """
    if not text:
        return SanitizationResult(
            sanitized_text="",
            original_length=0,
            sanitized_length=0,
            was_truncated=False,
            injection_patterns_found=0,
        )

    original_length = len(text)
    injection_count = 0

    # 1. Eliminar scripts, estilos y tags HTML
    cleaned = HTML_TAG_RE.sub(" ", text)

    # 2. Neutralizar etiquetas XML reservadas utilizadas en prompts
    for tag_pattern in RESERVED_XML_TAGS:
        cleaned = re.sub(tag_pattern, "[TAG_REMOVED]", cleaned, flags=re.IGNORECASE)

    # 3. Detectar y neutralizar patrones conocidos de Prompt Injection
    for pattern in PROMPT_INJECTION_PATTERNS:
        matches = re.findall(pattern, cleaned)
        if matches:
            injection_count += len(matches)
            cleaned = re.sub(pattern, "[INSTRUCTION_REMOVED]", cleaned)

    # 4. Normalizar espacios en blanco (múltiples saltos o espacios consecutivos)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n\s*\n+", "\n\n", cleaned).strip()

    # 5. Aplicar límite máximo de caracteres
    was_truncated = len(cleaned) > max_chars
    if was_truncated:
        cleaned = cleaned[:max_chars].rsplit(" ", 1)[0] + "..."

    return SanitizationResult(
        sanitized_text=cleaned,
        original_length=original_length,
        sanitized_length=len(cleaned),
        was_truncated=was_truncated,
        injection_patterns_found=injection_count,
    )
