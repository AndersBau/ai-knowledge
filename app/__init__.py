
from flask import Flask
from app.config import Config
from app.extensions import db
from app.routes.health import health_bp
from app.routes.documents import documents_bp
from app.routes.questions import questions_bp


def create_app():
  app = Flask(__name__)
  app.config.from_object(Config)

  db.init_app(app)

  app.register_blueprint(health_bp)
  app.register_blueprint(documents_bp)
  app.register_blueprint(questions_bp)

  return app
