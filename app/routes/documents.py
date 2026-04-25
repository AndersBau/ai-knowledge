from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Document

documents_bp = Blueprint("documents", __name__, url_prefix="/documents")

@documents_bp.route("", methods=["POST"])
def create_document():
    data = request.get_json() or {}

    title = data.get("title")

    if not title:
        return jsonify({"error": "Title is required."}), 400
    document = Document(title=title)
    db.session.add(document)
    db.session.commit()
    return jsonify({
        "id": document.id,
        "title": document.title,
        "created_at": document.created_at.isoformat()
        }), 201

@documents_bp.route("", methods=["GET"])
def list_documents():
    documents = Document.query.order_by(Document.created_at.desc()).all()

    return jsonify([
        {
            "id": document.id,
            "title": document.title,
            "s3_key": document.s3_key,
            "created_at": document.created_at.isoformat()
        } for document in documents
    ]), 200


@documents_bp.route("/<int:document_id>", methods=["PATCH"])
def update_document_title(document_id):
    data = request.get_json() or {}
    title = data.get("title")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Title is required."}), 400

    document = db.session.get(Document, document_id)
    if document is None:
        return jsonify({"error": "Document not found."}), 404

    document.title = title.strip()
    db.session.commit()

    return jsonify({
        "id": document.id,
        "title": document.title,
        "s3_key": document.s3_key,
        "created_at": document.created_at.isoformat()
    }), 200


@documents_bp.route("/<int:document_id>", methods=["DELETE"])
def delete_document(document_id):
    document = db.session.get(Document, document_id)

    if document is None:
        return jsonify({"error": "Document not found."}), 404

    db.session.delete(document)
    db.session.commit()
    return "", 204
