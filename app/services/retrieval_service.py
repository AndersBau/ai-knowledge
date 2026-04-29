from app.models import DocumentChunk

def retrieve_relevant_chunks(document_id: int, question: str, limit: int = 3) -> list[DocumentChunk]:
    question_words = set(question.lower().split())

    chunks = DocumentChunk.query.filter_by(document_id=document_id).all()

    scored_chunks = []

    for chunk in chunks:
        chunk_words = set(chunk.content.lower().split())
        score = len(question_words.intersection(chunk_words))
        scored_chunks.append((chunk, score))

        scored_chunks.sort(key=lambda item: item[0], reverse=True)

        return [
            chunk
            for chunk, score in scored_chunks[:limit]
            if score > 0
        ] or chunks[:limit]  # Fallback to first chunks if no relevant ones found