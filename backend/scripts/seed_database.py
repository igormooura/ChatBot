from app import create_app, db
from app.models.Doctor import Doctor
from app.models.Specialty import Specialty
from app.models.Patient import Patient
from app.models.Exam import Exam
from app.models.DoctorAvailability import DoctorAvailability
from app.models.ExamAvailability import ExamAvailability
from datetime import datetime, timedelta

DADOS_MEDICOS = {
    "Dr. Arnaldo Coração": ["Cardiologia", "Clínica Geral"],
    "Dra. Péricles Pele": ["Dermatologia"],
    "Dr. Osvaldo Osso": ["Ortopedia"],
    "Dra. Gabriela Gastão": ["Gastroenterologia", "Clínica Geral"],
    "Dr. Nelson Nervo": ["Neurologia"],
    "Dra. Otávia Olhos": ["Oftalmologia"],
    "Dr. Oto Rino": ["Otorrinolaringologia"],
    "Dra. Helena Hormônio": ["Endocrinologia"],
    "Dr. Paulo Pulmão": ["Pneumologia", "Clínica Geral"],
    "Dr. Ubiratan Uretra": ["Urologia"],
    "Dra. Gina Costa": ["Ginecologia"],
    "Dra. Geovana Geral": ["Clínica Geral"]
}

DADOS_PACIENTES = [
    {"nome": "Ana Silva", "cpf": "111.222.333-44", "email": "ana.silva@example.com"},
    {"nome": "Bruno Costa", "cpf": "222.333.444-55", "email": "bruno.costa@example.com"},
    {"nome": "Carla Dias", "cpf": "333.444.555-66", "email": "carla.dias@example.com"},
    {"nome": "Daniel Farias", "cpf": "444.555.666-77", "email": "daniel.farias@example.com"}
]

TIPOS_DE_EXAME = [
    "Hemograma Completo", "Glicemia de Jejum", "Perfil Lipídico (Colesterol Total e Frações)",
    "Ureia e Creatinina", "Ácido Úrico", "Urina Tipo I", "Exame Parasitológico de Fezes",
    "Eletrocardiograma (ECG)", "Ecocardiograma", "Teste Ergométrico (Esteira)", "Holter 24h", "M.A.P.A. 24h",
    "Raio-X do Tórax", "Ultrassonografia Abdominal", "Tomografia Computadorizada do Crânio",
    "Ressonância Magnética do Joelho", "Mamografia", "Densitometria Óssea",
    "Endoscopia Digestiva Alta", "Colonoscopia", "Papanicolau", "Exame de PSA (Próstata)",
    "Eletroencefalograma (EEG)", "Biópsia de Pele", "Exame de Fundo de Olho"
]


def popular_banco():
    app = create_app()
    with app.app_context():
        print("Recriando todas as tabelas do banco de dados...")
        db.drop_all()
        db.create_all()
        print("Tabelas recriadas com sucesso.")

        print("\nPopulando a tabela de Especialidades...")
        nomes_unicos_especialidades = set()
        for lista_especialidades in DADOS_MEDICOS.values():
            nomes_unicos_especialidades.update(lista_especialidades)
        
        for nome_especialidade in nomes_unicos_especialidades:
            nova_especialidade = Specialty(name=nome_especialidade)
            db.session.add(nova_especialidade)
        db.session.commit()
        print(f"  - {len(nomes_unicos_especialidades)} especialidades únicas foram adicionadas.")

        print("\nPopulando a tabela de Médicos e associando especialidades...")
        for nome_medico, lista_nomes_especialidades in DADOS_MEDICOS.items():
            novo_medico = Doctor(name=nome_medico)
            db.session.add(novo_medico)

            for nome_especialidade in lista_nomes_especialidades:
                especialidade_obj = db.session.query(Specialty).filter_by(name=nome_especialidade).first()
                if especialidade_obj:
                    novo_medico.specialties.append(especialidade_obj)
        
        db.session.commit()
        print(f"  - {len(DADOS_MEDICOS)} médicos foram adicionados e associados.")

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

        print("\nPopulando a tabela de Disponibilidade de Exames...")
        exames_no_banco = db.session.query(Exam).all()
        total_horarios_exame = 0
        dias_uteis = range(5)

        for exame in exames_no_banco:
            if any(keyword in exame.type for keyword in ["Glicemia de Jejum", "Perfil Lipídico"]):
                for dia in range(1, 8):
                    data_base = datetime.utcnow() + timedelta(days=dia)
                    if data_base.weekday() in dias_uteis:
                        for hora in range(7, 11):
                            for minuto in [0, 30]:
                                horario = ExamAvailability(
                                    exam_id=exame.id,
                                    date=data_base.replace(hour=hora, minute=minuto, second=0, microsecond=0)
                                )
                                db.session.add(horario)
                                total_horarios_exame += 1
            else:
                for dia in range(1, 8):
                    data_base = datetime.utcnow() + timedelta(days=dia)
                    if data_base.weekday() in dias_uteis:
                        for hora in range(8, 18):
                            if hora != 12:
                                for minuto in [0, 30]:
                                    horario = ExamAvailability(
                                        exam_id=exame.id,
                                        date=data_base.replace(hour=hora, minute=minuto, second=0, microsecond=0)
                                    )
                                    db.session.add(horario)
                                    total_horarios_exame += 1
        
        db.session.commit()
        print(f"  - {total_horarios_exame} horários de exame disponíveis foram adicionados.")

        print("\nPopulando a tabela de Disponibilidade de Médicos (com horário UTC)...")
        medicos = db.session.query(Doctor).all()
        total_horarios_medico = 0
        
        for medico in medicos:
            for dia in range(7): 
                data_base = datetime.utcnow() + timedelta(days=dia)
                for hora in range(9, 12):
                    horario = DoctorAvailability(doctor_id=medico.id, date=data_base.replace(hour=hora, minute=0, second=0, microsecond=0))
                    db.session.add(horario)
                    total_horarios_medico += 1
                for hora in range(14, 18):
                    horario = DoctorAvailability(doctor_id=medico.id, date=data_base.replace(hour=hora, minute=0, second=0, microsecond=0))
                    db.session.add(horario)
                    total_horarios_medico += 1

        db.session.commit()
        print(f"  - {total_horarios_medico} horários de consulta disponíveis foram adicionados.")

        print("\nBanco de dados populado com sucesso!")

if __name__ == "__main__":
    popular_banco()