# backend/run.py
from app import create_app, db
from sqlalchemy.exc import OperationalError  


app = create_app()

with app.app_context():
    print("-----------------------------------------------------")
    print("--- Verificando Conexão com o Banco de Dados... ---")
    
    try:
        db.create_all()
        print("✅ SUCESSO! Conexão com o banco de dados estabelecida.")
        print("✅ As tabelas foram verificadas e/ou criadas com sucesso.")

    except OperationalError as e:
        print("❌ FALHA AO CONECTAR: Verifique as credenciais e o host.")
        print("   - O container do PostgreSQL no Docker está rodando?")
        print("   - As variáveis DB_USER, DB_PASSWORD, DB_NAME e DB_HOST no seu .env estão corretas?")
        print("   - A porta do banco de dados está correta?")
        print(f"\n   Detalhe do Erro: {e}")

    except Exception as e:
        # Captura qualquer outro erro inesperado durante o processo.
        print(f"❌ FALHA: Um erro inesperado ocorreu: {e}")
    
    print("-----------------------------------------------------")


if __name__ == '__main__':
    print("\nIniciando o servidor Flask. Pressione Ctrl+C para parar.")
    app.run(host='0.0.0.0', port=5000, debug=False)