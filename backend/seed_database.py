
from app import create_app, db
from app.models.Doctor import Doctor
from app.models.Patient import Patient
from app.models.Exam import Exam
from app.models.DoctorAvailability import DoctorAvailability
from datetime import datetime, timedelta


DADOS_MEDICOS = {
    "Cardiologia": "Dr. Arnaldo Coração",
    "Dermatologia": "Dra. Péricles Pele",
    "Ortopedia": "Dr. Osvaldo Osso",
    "Clínica Geral": "Dra. Geovana Geral",
    "Pediatria": "Dr. Ciro Criança"
}

DADOS_PACIENTES = [
    {"nome": "Ana Silva", "cpf": "111.222.333-44", "email": "ana.silva@example.com"},
    {"nome": "Bruno Costa", "cpf": "222.333.444-55", "email": "bruno.costa@example.com"},
    {"nome": "Carla Dias", "cpf": "333.444.555-66", "email": "carla.dias@example.com"},
    {"nome": "Daniel Farias", "cpf": "444.555.666-77", "email": "daniel.farias@example.com"}
]

TIPOS_DE_EXAME = [
     "Hemograma Completo",
     "Raio-X do Tórax",
     "Ecocardiograma",
     "Ultrassonografia Abdominal",
     "Tomografia Computadorizada",
     "Ressonância Magnética",
     "Eletrocardiograma (ECG)"
]

def popular_banco():
    """
    Recria o banco de dados e o popula com dados de exemplo para Médicos, Pacientes,
    Exames e, mais importante, a Disponibilidade dos Médicos (usando UTC).
    """
    app = create_app()
    with app.app_context():
        print("Recriando todas as tabelas do banco de dados...")
        db.drop_all()
        db.create_all()
        print("Tabelas recriadas com sucesso.")


        print("\nPopulando a tabela de Médicos...")
        for especialidade, nome in DADOS_MEDICOS.items():
            novo_medico = Doctor(name=nome, specialty=especialidade)
            db.session.add(novo_medico)
        db.session.commit()
        print(f"  - {len(DADOS_MEDICOS)} médicos foram adicionados.")

        print("\nPopulando a tabela de Pacientes...")
        for dados_paciente in DADOS_PACIENTES:
            novo_paciente = Patient(
                name=dados_paciente["nome"],
                cpf=dados_paciente["cpf"],
                email=dados_paciente["email"]
            )
            db.session.add(novo_paciente)
        db.session.commit()
        print(f"  - {len(DADOS_PACIENTES)} pacientes foram adicionados.")

        print("\nPopulando a tabela de Exames...")
        for tipo_exame in TIPOS_DE_EXAME:
            novo_exame = Exam(type=tipo_exame)
            db.session.add(novo_exame)
        db.session.commit()
        print(f"  - {len(TIPOS_DE_EXAME)} tipos de exame foram adicionados.")

        print("\nPopulando a tabela de Disponibilidade de Médicos (com horário UTC)...")
        medicos = db.session.query(Doctor).all()
        total_horarios = 0
        
        for medico in medicos:
            for dia in range(7): 
                data_base = datetime.utcnow() + timedelta(days=dia)
                for hora in range(9, 12):
                    horario = DoctorAvailability(doctor_id=medico.id, date=data_base.replace(hour=hora, minute=0, second=0, microsecond=0))
                    db.session.add(horario)
                    total_horarios += 1
                for hora in range(14, 18):
                    horario = DoctorAvailability(doctor_id=medico.id, date=data_base.replace(hour=hora, minute=0, second=0, microsecond=0))
                    db.session.add(horario)
                    total_horarios += 1

        db.session.commit()
        print(f"  - {total_horarios} horários disponíveis foram adicionados.")

        print("\nBanco de dados populado com sucesso!")

if __name__ == "__main__":
    popular_banco()