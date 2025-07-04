
from app import create_app, db
from app.models import Doctor, Availability
from datetime import datetime, timedelta

DADOS_MEDICOS = [
    {"nome": "Dr. Arnaldo Coração", "especialidade": "Cardiologista"},
    {"nome": "Dra. Péricles Pele", "especialidade": "Dermatologista"},
    {"nome": "Dr. Osvaldo Osso", "especialidade": "Ortopedista"},
    {"nome": "Dra. Geovana Geral", "especialidade": "Clínico Geral"}
]

def popular_banco_dinamico():
    app = create_app()
    with app.app_context():
        print("Iniciando o script para popular o banco de dados...")
        
        print("Limpando tabelas Doctor e Availability...")
        db.session.query(Availability).delete()
        db.session.query(Doctor).delete()
        db.session.commit()
        print("Tabelas limpas.")

        print("Populando o banco de dados com horários dinâmicos...")
        hoje = datetime.now()

        for dados_medico in DADOS_MEDICOS:
            novo_medico = Doctor(name=dados_medico["nome"], specialty=dados_medico["especialidade"])
            db.session.add(novo_medico)
            db.session.flush()

            horarios_gerados = []
            for dias_a_frente in range(1, 4):
                data_futura = hoje + timedelta(days=dias_a_frente)
                horarios_gerados.append(data_futura.replace(hour=10, minute=30, second=0, microsecond=0))
                horarios_gerados.append(data_futura.replace(hour=15, minute=0, second=0, microsecond=0))

            for horario in horarios_gerados:
                nova_disponibilidade = Availability(doctor_id=novo_medico.id, date=horario)
                db.session.add(nova_disponibilidade)
            
            print(f"  - Médico '{dados_medico['nome']}' e suas disponibilidades futuras foram adicionados.")

        db.session.commit()
        print("\nBanco de dados populado com sucesso!")

if __name__ == "__main__":
    popular_banco_dinamico()