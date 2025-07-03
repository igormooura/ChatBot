# backend/seed_database.py

from app import create_app, db
from app.models import Doctor, Availability
from datetime import datetime, timedelta

DADOS_EXEMPLO = {
    "Cardiologista": {
        "nome": "Dr. Arnaldo Coração",
        "horarios": ["2025-07-10 10:00", "2025-07-10 11:00", "2025-07-11 15:00"]
    },
    "Dermatologista": {
        "nome": "Dra. Péricles Pele",
        "horarios": ["2025-07-12 09:00", "2025-07-12 14:00"]
    },
    "Ortopedista": {
        "nome": "Dr. Osvaldo Osso",
        "horarios": ["2025-07-11 11:00", "2025-07-15 14:00"]
    },
    "Clínico Geral": {
        "nome": "Dra. Geovana Geral",
        "horarios": ["2025-07-10 08:00", "2025-07-11 08:00", "2025-07-12 08:00"]
    }
}

def popular_banco():
    app = create_app()
    with app.app_context():
        print("Limpando tabelas Doctor e Availability...")
        db.session.query(Availability).delete()
        db.session.query(Doctor).delete()
        db.session.commit()
        print("Tabelas limpas.")

        print("Populando o banco de dados...")
        for especialidade, dados in DADOS_EXEMPLO.items():
            novo_medico = Doctor(name=dados["nome"], specialty=especialidade)
            db.session.add(novo_medico)
            db.session.flush()

            for horario_str in dados["horarios"]:
                horario_dt = datetime.strptime(horario_str, "%Y-%m-%d %H:%M")
                nova_disponibilidade = Availability(doctor_id=novo_medico.id, date=horario_dt)
                db.session.add(nova_disponibilidade)
            
            print(f"  - Médico '{dados['nome']}' e suas disponibilidades foram adicionados.")

        db.session.commit()
        print("\nBanco de dados populado com sucesso!")

if __name__ == "__main__":
    popular_banco()