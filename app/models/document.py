from datetime import datetime, timezone
from app.extensions import db

class Document(db.Model):
  __tablename__ = "documents"

  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(255), nullable=False)
  content = db.Column(db.Text, nullable=False)
  s3_key = db.Column(db.String(500), nullable=True)
  created_at = db.Column(
    db.DateTime,
    nullable=False,
    default=lambda: datetime.now(timezone.utc)
  )
