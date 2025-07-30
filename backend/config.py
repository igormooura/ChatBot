# config.py

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

print("--- Iniciando Configuração do Projeto ---")

# Carrega as variáveis de ambiente do ficheiro .env
# A função load_dotenv() é inteligente e procura o .env na pasta atual e nas pastas-mãe.
load_dotenv()

# --- Configurações de IA ---
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_HTTP_PORT = 6333
QDRANT_GRPC_PORT = 6334
COLLECTION_NAME = "especialidades_medicas"
EMBEDDING_MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'

# --- Inicialização dos Módulos de IA ---
qdrant_client = None
embedding_model = None
gemini_model = None
qdrant_ready = False
gemini_ready = False

# 1. Configurar Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
        print("✅ API do Gemini configurada com sucesso.")
        gemini_ready = True
    except Exception as e:
        print(f"❌ ERRO ao configurar a API do Gemini: {e}")
else:
    print("⚠️ ALERTA: Chave de API do Gemini (GEMINI_API_KEY) não encontrada no arquivo .env.")

# 2. Configurar Qdrant e SentenceTransformer
try:
    print(f"Conectando ao Qdrant (HTTP em {QDRANT_HOST}:{QDRANT_HTTP_PORT})...")
    qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_HTTP_PORT)
    qdrant_client.get_collection(collection_name=COLLECTION_NAME) # Testa conexão e se a coleção existe
    print(f"✅ Conectado com sucesso à coleção '{COLLECTION_NAME}' no Qdrant.")
    
    print(f"Carregando o modelo de embedding '{EMBEDDING_MODEL_NAME}'...")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print("✅ Modelo de embedding carregado.")
    qdrant_ready = True
except Exception as e:
    print(f"❌ ERRO CRÍTICO QDRANT: Não foi possível conectar ao Qdrant ou carregar o modelo de embedding. Detalhes: {e}")

print("--- Configuração Concluída ---")