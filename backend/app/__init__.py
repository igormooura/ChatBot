# backend/app/__init__.py
import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from config import qdrant_ready, gemini_ready
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

load_dotenv()


db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')
db_port = os.getenv('DB_PORT')

def create_app():
    app = Flask(__name__)
    CORS(app)

    DATABASE_URI = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    
    db.init_app(app)


    from . import models


    print("--- Status dos Serviços de IA ---")
    print(f"Gemini (LLM) pronto: {'Sim' if gemini_ready else 'Não'}")
    print(f"Qdrant (Busca Vetorial) pronto: {'Sim' if qdrant_ready else 'Não'}")
    print("---------------------------------")


    from .router.agendamento_routes import bp as agendamento_blueprint
    app.register_blueprint(agendamento_blueprint)

    @app.route('/health')
    def health_check():
        return "Servidor backend do chatbot está no ar!"

    return app