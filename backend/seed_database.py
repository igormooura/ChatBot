from app import create_app, db
from app.models.Doctor import Doctor
from app.models.Patient import Patient
from app.models.Exam import Exam
from app.models.DoctorAvailability import DoctorAvailability
from app.models.ExamAvailability import ExamAvailability  # <-- IMPORTAÇÃO ADICIONADA
from datetime import datetime, timedelta

# DADOS DOS MÉDICOS ATUALIZADOS
DADOS_MEDICOS = {
    "Cardiologia": "Dr. Arnaldo Coração",
    "Dermatologia": "Dra. Péricles Pele",
    "Ortopedia": "Dr. Osvaldo Osso",
    "Gastroenterologia": "Dra. Gabriela Gastão",
    "Neurologia": "Dr. Nelson Nervo",
    "Oftalmologia": "Dra. Otávia Olhos",
    "Otorrinolaringologia": "Dr. Oto Rino",
    "Endocrinologia": "Dra. Helena Hormônio",
    "Pneumologia": "Dr. Paulo Pulmão",
    "Urologia": "Dr. Ubiratan Uretra",
    "Ginecologia": "Dra. Gina Costa",
    "Clínica Geral": "Dra. Geovana Geral"
}

DADOS_PACIENTES = [
    {"nome": "Ana Silva", "cpf": "111.222.333-44", "email": "ana.silva@example.com"},
    {"nome": "Bruno Costa", "cpf": "222.333.444-55", "email": "bruno.costa@example.com"},
    {"nome": "Carla Dias", "cpf": "333.444.555-66", "email": "carla.dias@example.com"},
    {"nome": "Daniel Farias", "cpf": "444.555.666-77", "email": "daniel.farias@example.com"}
]

# LISTA DE EXAMES EXPANDIDA
TIPOS_DE_EXAME = [
    # Exames Gerais e de Sangue
    "Hemograma Completo",
    "Glicemia de Jejum",
    "Perfil Lipídico (Colesterol Total e Frações)",
    "Ureia e Creatinina",
    "Ácido Úrico",
    "Urina Tipo I",
    "Exame Parasitológico de Fezes",

    # Exames Cardiológicos
    "Eletrocardiograma (ECG)",
    "Ecocardiograma",
    "Teste Ergométrico (Esteira)",
    "Holter 24h",
    "M.A.P.A. 24h",

    # Imagem
    "Raio-X do Tórax",
    "Ultrassonografia Abdominal",
    "Tomografia Computadorizada do Crânio",
    "Ressonância Magnética do Joelho",
    "Mamografia",
    "Densitometria Óssea",

    # Outras Especialidades
    "Endoscopia Digestiva Alta",
    "Colonoscopia",
    "Papanicolau",
    "Exame de PSA (Próstata)",
    "Eletroencefalograma (EEG)",
    "Biópsia de Pele",
    "Exame de Fundo de Olho"
]

def popular_banco():
    """
    Recria o banco de dados e o popula com dados de exemplo para Médicos, Pacientes,
    Exames, Disponibilidade de Exames e Disponibilidade de Médicos.
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

        # --- SEÇÃO NOVA E CORRIGIDA ---
        print("\nPopulando a tabela de Disponibilidade de Exames...")
        exames_no_banco = db.session.query(Exam).all()
        total_horarios_exame = 0
        dias_uteis = range(5)  # Segunda a Sexta (0 a 4)

        for exame in exames_no_banco:
            # Regra 1: Exames de jejum (ex: Glicemia), apenas no período da manhã.
            if any(keyword in exame.type for keyword in ["Glicemia de Jejum", "Perfil Lipídico"]):
                for dia in range(1, 8):  # Para os próximos 7 dias
                    data_base = datetime.utcnow() + timedelta(days=dia)
                    if data_base.weekday() in dias_uteis:
                        for hora in range(7, 11):  # Das 7:00 às 10:30
                            for minuto in [0, 30]:
                                horario = ExamAvailability(
                                    exam_id=exame.id,
                                    date=data_base.replace(hour=hora, minute=minuto, second=0, microsecond=0)
                                )
                                db.session.add(horario)
                                total_horarios_exame += 1
            # Regra 2: Para todos os outros exames, horário comercial padrão.
            else:
                for dia in range(1, 8):
                    data_base = datetime.utcnow() + timedelta(days=dia)
                    if data_base.weekday() in dias_uteis:
                        for hora in range(8, 18):
                            if hora != 12:  # Pular horário de almoço
                                for minuto in [0, 30]:
                                    horario = ExamAvailability(
                                        exam_id=exame.id,
                                        date=data_base.replace(hour=hora, minute=minuto, second=0, microsecond=0)
                                    )
                                    db.session.add(horario)
                                    total_horarios_exame += 1
        
        db.session.commit()
        print(f"  - {total_horarios_exame} horários de exame disponíveis foram adicionados.")
        # --- FIM DA SEÇÃO NOVA ---

        print("\nPopulando a tabela de Disponibilidade de Médicos (com horário UTC)...")
        medicos = db.session.query(Doctor).all()
        total_horarios_medico = 0
        
        for medico in medicos:
            for dia in range(7): 
                data_base = datetime.utcnow() + timedelta(days=dia)
                # Horários da manhã
                for hora in range(9, 12):
                    horario = DoctorAvailability(doctor_id=medico.id, date=data_base.replace(hour=hora, minute=0, second=0, microsecond=0))
                    db.session.add(horario)
                    total_horarios_medico += 1
                # Horários da tarde
                for hora in range(14, 18):
                    horario = DoctorAvailability(doctor_id=medico.id, date=data_base.replace(hour=hora, minute=0, second=0, microsecond=0))
                    db.session.add(horario)
                    total_horarios_medico += 1

        db.session.commit()
        print(f"  - {total_horarios_medico} horários de consulta disponíveis foram adicionados.")

        print("\nBanco de dados populado com sucesso!")

if __name__ == "__main__":
    popular_banco()