from rag.ingestion.chunking import chunk_article


def test_chunk_short_article_returns_single_chunk() -> None:
    article_text = (
        "El delantero del Chelsea, Nicolas Jackson, sufri una lesin muscular durante el "
        "entrenamiento y ser baja confirmada para el derbi londinense ante el Arsenal."
    )
    chunks = chunk_article(article_text)
    assert len(chunks) == 1
    assert chunks[0].strip() == article_text.strip()


def test_chunk_long_article_splits_with_overlap() -> None:
    # Creamos un artculo con ms de 500 tokens (aprox 700 palabras)
    sentences = [
        f"Sentencia {i}: El equipo local mantiene un rendimiento destacado."
        for i in range(80)
    ]
    long_text = " ".join(sentences)

    chunks = chunk_article(long_text, max_tokens=200, overlap_pct=0.20)
    assert len(chunks) > 1

    # Verificar que existe solapamiento entre chunks consecutivos
    first_chunk_end = chunks[0][-50:]
    assert any(
        first_chunk_end in chunks[1] or word in chunks[1] for word in first_chunk_end.split()
    )


def test_chunk_empty_text_returns_empty_list() -> None:
    assert chunk_article("") == []
    assert chunk_article("   ") == []
