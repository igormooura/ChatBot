# backend/sas.py (ou test_connection.py)
import os
from dotenv import load_dotenv
import pg8000.dbapi

print("--- Iniciando Teste de Conexão Pura com pg8000 ---")
load_dotenv()

db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')
db_port = 5433 # A NOVA PORTA

print(f"Tentando conectar com: user='{db_user}', host='{db_host}', port={db_port}, database='{db_name}'")

try:
    conn = pg8000.dbapi.connect(
        user=db_user,
        password=db_password,
        host=db_host,
        database=db_name,
        port=db_port # <--- MUDANÇA AQUI
    )
    print("\n✅✅✅ VITÓRIA! A CONEXÃO FUNCIONOU! ✅✅✅")
    conn.close()

except Exception as e:
    print(f"\n❌❌❌ FALHA! Um erro inesperado ocorreu. ❌❌❌")
    print(f"Erro: {e}")