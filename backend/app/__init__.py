# backend/app/__init__.py

import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from config import qdrant_ready, gemini_ready
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

# 1. Inicializa as extensões (sem o app ainda)
db = SQLAlchemy()
mail = Mail()

# 2. Carrega as variáveis de ambiente do arquivo .env
load_dotenv()
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')

def create_app():
    app = Flask(__name__)
    CORS(app)

    # --- 3. BLOCO ÚNICO DE CONFIGURAÇÕES ---
    # Coloque TODAS as configurações do app aqui, juntas.
    
    # Configurações do Banco de Dados
    DATABASE_URI = f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}"
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configurações de Upload
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

    # Configurações do Flask-Mail
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')
    # --- FIM DO BLOCO DE CONFIGURAÇÕES ---

    # 4. Agora que o app está configurado, inicialize as extensões com ele.
    db.init_app(app)
    mail.init_app(app)

    # 5. Lógica adicional e registro de rotas
    
    # Cria a pasta de uploads se não existir
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Importa os modelos (importante para o SQLAlchemy criar as tabelas)
    from . import models

    print("--- Status dos Serviços de IA ---")
    print(f"Gemini (LLM) pronto: {'Sim' if gemini_ready else 'Não'}")
    print(f"Qdrant (Busca Vetorial) pronto: {'Sim' if qdrant_ready else 'Não'}")
    print("---------------------------------")

    # Importa e registra todos os blueprints (rotas)
    from .router.agendamento_routes import bp as agendamento_blueprint
    app.register_blueprint(agendamento_blueprint)
    
    from .router.exame_routes import bp as exame_blueprint
    app.register_blueprint(exame_blueprint)
    
    from .router.auth_routes import bp as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .router.upload_pdf import bp as upload_blueprint
    app.register_blueprint(upload_blueprint)
    
    @app.route('/health')
    def health_check():
        return "Servidor backend do chatbot está no ar!"

    return app