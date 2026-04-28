from flask import Blueprint, request, jsonify, current_app
from app.models import Document
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

    context = f"""
    Document Title: {document.title}
    Document Content: {document.content}
"""

    response = client.responses.create(
        model="gpt-5.4-mini",
        instructions="Answer the question based on the provided document context.",
        input=f"Context:\n{context}\n\nQuestion:\n{question}"
    )

    return jsonify({"answer": response.output_text}), 200