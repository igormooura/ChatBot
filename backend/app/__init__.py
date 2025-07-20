# backend/app/__init__.py

import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from config import qdrant_ready, gemini_ready
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail


db = SQLAlchemy()
mail = Mail()

load_dotenv()

db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')

def create_app():
    app = Flask(__name__)
    CORS(app)

    DATABASE_URI = f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}"
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    mail.init_app(app)

    # Uploads
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    from .router.upload_pdf import bp as upload_blueprint
    app.register_blueprint(upload_blueprint)

    # Configurações do Flask-Mail a partir do .env
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')
    app.config['SECRET_KEY_EMAIL'] = os.getenv('SECRET_KEY_EMAIL')

    from . import models

    print("--- Status dos Serviços de IA ---")
    print(f"Gemini (LLM) pronto: {'Sim' if gemini_ready else 'Não'}")
    print(f"Qdrant (Busca Vetorial) pronto: {'Sim' if qdrant_ready else 'Não'}")
    print("---------------------------------")

    # Importa o blueprint da subpasta /app/router/
    from .router.agendamento_routes import bp as agendamento_blueprint
    app.register_blueprint(agendamento_blueprint)
    from .router.exame_routes import bp as exame_blueprint
    app.register_blueprint(exame_blueprint)
    from .router.auth_routes import bp as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    
    @app.route('/health')
    def health_check():
        return "Servidor backend do chatbot está no ar!"

    return app