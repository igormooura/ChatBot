# backend/app/__init__.py

from flask import Flask
from flask_cors import CORS
from config import qdrant_ready, gemini_ready

def create_app():
    app = Flask(__name__)
    CORS(app)

    print("--- Status dos Serviços de IA ---")
    print(f"Gemini (LLM) pronto: {'Sim' if gemini_ready else 'Não'}")
    print(f"Qdrant (Busca Vetorial) pronto: {'Sim' if qdrant_ready else 'Não'}")
    print("---------------------------------")

    # Importa o blueprint da subpasta /app/router/
    from .router.agendamento_routes import bp as agendamento_blueprint
    app.register_blueprint(agendamento_blueprint)

    @app.route('/health')
    def health_check():
        return "Servidor backend do chatbot está no ar!"

    return app