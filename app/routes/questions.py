from flask import Blueprint, request, jsonify, current_app
from app.services.retrieval_service import retrieve_relevant_chunks
from app.models import Document, chunk
from openai import OpenAI
import os

questions_bp = Blueprint("questions", __name__)



@questions_bp.route("/ask", methods=["POST"])
def ask_question():
    data = request.get_json() or {}

    document_id = data.get("document_id")
    question = data.get("question")

    if not document_id or not question:
        return jsonify({"error": "Document ID and question are required."}), 400
    
    document = Document.query.get(document_id)
    if not document:
        return jsonify({"error": "Document not found."}), 404
    
    api_key = current_app.config.get("OPENAI_API_KEY")

    if not api_key:
        return jsonify({"error": "OpenAI API key not configured."}), 500

    client = OpenAI(api_key=api_key)

    relevant_chunks = retrieve_relevant_chunks(document_id, question)

    context = "\n\n".join(
        [
            f"Chunk {chunk.chunk_index}:\n{chunk.content}"
            for chunk in relevant_chunks
        ]
    )

    response = client.responses.create(
        model="gpt-5.4-mini",
        instructions=(
            "Answer the question using only the provided context. "
            "If the answer is not in the context, say you do not know based on the document."
    ),    
    input=f"Document Title: {document.title}\n\nContext:\n{context}\n\nQuestion: {question}",
    max_output_tokens=300
    )

    return jsonify({
        "answer": response.output_text,
        "sources": [
            {
                "chunk_index": chunk.chunk_index,
                "content": chunk.content
            } for chunk in relevant_chunks
        ]
        }), 200