# backend/run.py
from app import create_app, db

app = create_app()

with app.app_context():
    print("Criando tabelas no banco de dados...")
    db.create_all()
    print("Tabelas criadas com sucesso!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)