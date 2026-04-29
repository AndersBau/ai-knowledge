from datetime import datetime, timezone
from app.extensions import db

class DocumentChunk(db.Model):
    __tablename__ = "document_chunks"

    id = db.Column(db.Integer, primary_key=True)

    document_id = db.Column(
        db.Integer, 
        db.ForeignKey("documents.id"), nullable=False
        )
    
    chunk_index = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
        )