from app import create_app, db
# Importe todos os modelos que você deseja popular
from app.models.Doctor import Doctor
from app.models.Patient import Patient
from app.models.User import User
from app.models.Exam import Exam
# Não precisamos importar os modelos de disponibilidade, pois não vamos populá-los

# --- DADOS DE EXEMPLO AMPLIADOS ---

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
    Recria o banco de dados e o popula com dados de exemplo para todas as
    entidades principais, exceto as tabelas de disponibilidade.
    """
    app = create_app()
    with app.app_context():
        print("Recriando todas as tabelas do banco de dados...")
        db.drop_all()
        db.create_all()
        print("Tabelas recriadas com sucesso.")

        # --- Populando Médicos ---
        print("\nPopulando a tabela de Médicos...")
        for especialidade, nome in DADOS_MEDICOS.items():
            novo_medico = Doctor(name=nome, specialty=especialidade)
            db.session.add(novo_medico)
        db.session.commit()
        print(f"  - {len(DADOS_MEDICOS)} médicos foram adicionados.")

        # --- Populando Pacientes e Usuários vinculados ---
        print("\nPopulando as tabelas de Pacientes e Usuários...")
        for dados_paciente in DADOS_PACIENTES:
            # 1. Cria o usuário primeiro, mas não o salva ainda
            novo_usuario = User(
                username=dados_paciente["nome"].split()[0].lower(), # ex: 'ana'
                email=dados_paciente["email"]
            )
            # CORREÇÃO: A senha agora é definida, gerando o hash necessário.
            novo_usuario.set_password("senha123")
            
            # 2. Cria o paciente
            novo_paciente = Patient(name=dados_paciente["nome"], cpf=dados_paciente["cpf"])
            
            # 3. Associa os dois objetos. O SQLAlchemy cuidará das chaves estrangeiras.
            # Esta linha garante que tanto `user.patient_id` quanto `patient.user_id`
            # serão preenchidos corretamente antes de salvar.
            novo_paciente.user = novo_usuario

            # 4. Adiciona ambos à sessão. O flush/commit não é mais necessário aqui dentro.
            db.session.add(novo_usuario)
            db.session.add(novo_paciente)

        # 5. Faz um único commit para salvar todos os novos pacientes e usuários.
        db.session.commit()
        print(f"  - {len(DADOS_PACIENTES)} pacientes e usuários correspondentes foram adicionados.")

        # --- Populando Tipos de Exames ---
        print("\nPopulando a tabela de Exames...")
        for tipo_exame in TIPOS_DE_EXAME:
            novo_exame = Exam(type=tipo_exame)
            db.session.add(novo_exame)
        db.session.commit()
        print(f"  - {len(TIPOS_DE_EXAME)} tipos de exame foram adicionados.")

        # --- Confirmação Final ---
        # As tabelas de disponibilidade (DoctorAvailability, ExamAvailability)
        # e as de agendamento (Appointment, ScheduledExam) permanecem vazias,
        # prontas para serem preenchidas pela lógica da aplicação.
        
        print("\nBanco de dados populado com sucesso!")
        print("As tabelas de disponibilidade e agendamentos estão vazias, como solicitado.")

if __name__ == "__main__":
    popular_banco()
