import os

class Config:
  SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
  DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
  OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
  SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL",
    "sqlite:///app.db"
    )
  SQLALCHEMY_TRACK_MODIFICATIONS = False
