def split_text(text: str, max_words: int = 120) -> list[str]:
    words = text.split()

    chunks = []

    for i in range(0, len(words), max_words):
        chunk_words = words[i:i + max_words]
        chunks.append(" ".join(chunk_words))

    return chunks