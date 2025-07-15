# backend/app/services/exame_scheduling_service.py

from datetime import datetime, date, timedelta
from sqlalchemy import func

# Importe o 'db' e os modelos do seu projeto
from .. import db
from ..models.Exam import Exam
from ..models.ExamAvailability import ExamAvailability
from ..models.ScheculedExam import ScheduledExam
from ..models.Appointment import Appointment

# Constantes de negócio
EXAM_DURATION = timedelta(minutes=30)
WORK_START_HOUR = 8
WORK_END_HOUR = 18

# --- FUNÇÕES AUXILIARES (LÓGICA DE NEGÓCIO COM QUERIES REAIS) ---

def _generate_default_slots_for_day(target_date: date) -> list[datetime]:
    """Gera slots de 30 min para um dia de trabalho padrão (08:00 - 18:00)."""
    slots = []
    current_slot = datetime.combine(target_date, datetime.min.time()).replace(hour=WORK_START_HOUR)
    end_of_work = current_slot.replace(hour=WORK_END_HOUR)
    while current_slot < end_of_work:
        slots.append(current_slot)
        current_slot += EXAM_DURATION
    return slots

def _fetch_exam_availability_or_default(target_date: date, exam_id: int) -> list[datetime]:
    """Busca a disponibilidade de um exame no DB. Se vazia, retorna um horário padrão."""
    availabilities = db.session.query(ExamAvailability.date).filter(
        ExamAvailability.exam_id == exam_id,
        func.date(ExamAvailability.date) == target_date
    ).all()
    
    # .all() retorna uma lista de tuplas, ex: [(datetime.datetime(...)), ...]. Precisamos extrair o primeiro item.
    availability_dates = [item[0] for item in availabilities]
    
    if availability_dates:
        return sorted(availability_dates)

    return _generate_default_slots_for_day(target_date)

def _get_patient_commitments(target_date: date, patient_id: int) -> list[datetime]:
    """Busca todos os compromissos (consultas + exames) de um paciente."""
    commitments = set()
    
    # Consultas
    appointments = db.session.query(Appointment.date).filter(
        Appointment.patient_id == patient_id,
        func.date(Appointment.date) == target_date
    ).all()
    for appt in appointments:
        commitments.add(appt[0])

    # Exames
    scheduled_exams = db.session.query(ScheduledExam.date).filter(
        ScheduledExam.patient_id == patient_id,
        func.date(ScheduledExam.date) == target_date
    ).all()
    for exam in scheduled_exams:
        commitments.add(exam[0])
        
    return sorted(list(commitments))
    
def _is_slot_globally_taken(slot_time: datetime, exam_id: int) -> bool:
    """Verifica se um slot específico já foi agendado por QUALQUER paciente."""
    return db.session.query(ScheduledExam).filter_by(date=slot_time, exam_id=exam_id).first() is not None

# --- FUNÇÃO PRINCIPAL DO SERVIÇO ---

def find_and_schedule_sequential_exams(patient_id: int, exam_names: list[str]) -> list[datetime] | None:
    """
    Encontra o primeiro bloco de horários para agendar exames em sequência e o agenda.
    """
    if not exam_names:
        return None

    # Converte nomes de exames para IDs
    exam_objects = db.session.query(Exam).filter(Exam.type.in_(exam_names)).all()
    if len(exam_objects) != len(exam_names):
        # Lançar um erro ou logar que alguns exames não foram encontrados
        raise ValueError("Um ou mais tipos de exame não foram encontrados no banco de dados.")

    # Mapeia nome para ID para manter a ordem correta
    exam_id_map = {exam.type: exam.id for exam in exam_objects}
    exam_ids_in_order = [exam_id_map[name] for name in exam_names]

    target_date = date.today() + timedelta(days=1)
    patient_commitments = _get_patient_commitments(target_date, patient_id)
    first_exam_id = exam_ids_in_order[0]
    possible_start_slots = _fetch_exam_availability_or_default(target_date, first_exam_id)

    for block_start in possible_start_slots:
        current_slot_time = block_start
        is_block_viable = True
        
        for exam_id in exam_ids_in_order:
            slot_end = current_slot_time + EXAM_DURATION
            
            exam_specific_availability = _fetch_exam_availability_or_default(target_date, exam_id)
            if current_slot_time not in exam_specific_availability:
                is_block_viable = False
                break

            for commitment_start in patient_commitments:
                commitment_end = commitment_start + EXAM_DURATION
                if current_slot_time < commitment_end and slot_end > commitment_start:
                    is_block_viable = False
                    break
            if not is_block_viable: break

            if _is_slot_globally_taken(current_slot_time, exam_id):
                is_block_viable = False
                break
            
            current_slot_time += EXAM_DURATION

        if is_block_viable:
            # BLOCO ENCONTRADO! AGENDAR USANDO UMA TRANSAÇÃO.
            try:
                scheduled_times = []
                current_time_for_scheduling = block_start
                for exam_id in exam_ids_in_order:
                    new_exam = ScheduledExam(
                        patient_id=patient_id, 
                        exam_id=exam_id, 
                        date=current_time_for_scheduling,
                        # Adicione outros campos se necessário, como 'status'
                    )
                    db.session.add(new_exam)
                    scheduled_times.append(current_time_for_scheduling)
                    current_time_for_scheduling += EXAM_DURATION
                
                db.session.commit()
                return scheduled_times
            except Exception as e:
                db.session.rollback()
                print(f"ERRO DE BANCO DE DADOS: {e}")
                # Lançar um erro mais específico da aplicação se desejar
                raise
    
    return None # Nenhum bloco de horário foi encontrado