from datetime import datetime, date, timedelta
from sqlalchemy import func
import itertools 

from .. import db
from ..models.Exam import Exam
from ..models.ExamAvailability import ExamAvailability
from ..models.ScheculedExam import ScheduledExam
from ..models.Appointment import Appointment

EXAM_DURATION = timedelta(minutes=30)
WORK_START_HOUR = 8
WORK_END_HOUR = 18

def _generate_default_slots_for_day(target_date: date) -> list[datetime]:
    slots = []
    current_slot = datetime.combine(target_date, datetime.min.time()).replace(hour=WORK_START_HOUR)
    end_of_work = current_slot.replace(hour=WORK_END_HOUR)
    while current_slot < end_of_work:
        slots.append(current_slot)
        current_slot += EXAM_DURATION
    return slots

def _fetch_exam_availability_or_default(target_date: date, exam_id: int) -> list[datetime]:
    availabilities = db.session.query(ExamAvailability.date).filter(
        ExamAvailability.exam_id == exam_id,
        func.date(ExamAvailability.date) == target_date
    ).all()
    availability_dates = [item[0] for item in availabilities]
    if availability_dates:
        return sorted(availability_dates)
    return _generate_default_slots_for_day(target_date)

def _get_patient_commitments(target_date: date, patient_id: int) -> list[datetime]:
    commitments = set()
    appointments = db.session.query(Appointment.date).filter(
        Appointment.patient_id == patient_id, func.date(Appointment.date) == target_date
    ).all()
    for appt in appointments: commitments.add(appt[0])
    scheduled_exams = db.session.query(ScheduledExam.date).filter(
        ScheduledExam.patient_id == patient_id, func.date(ScheduledExam.date) == target_date
    ).all()
    for exam in scheduled_exams: commitments.add(exam[0])
    return sorted(list(commitments))
    
def _is_slot_globally_taken(slot_time: datetime, exam_id: int) -> bool:
    return db.session.query(ScheduledExam).filter_by(date=slot_time, exam_id=exam_id).first() is not None

def _check_block_viability(block_start_time: datetime, ordered_exam_ids: list[int], patient_id: int) -> bool:
    target_date = block_start_time.date()
    patient_commitments = _get_patient_commitments(target_date, patient_id)
    current_slot_time = block_start_time
    
    for exam_id in ordered_exam_ids:
        slot_end = current_slot_time + EXAM_DURATION
        
        exam_specific_availability = _fetch_exam_availability_or_default(target_date, exam_id)
        if current_slot_time not in exam_specific_availability: return False

        for commitment_start in patient_commitments:
            commitment_end = commitment_start + EXAM_DURATION
            if current_slot_time < commitment_end and slot_end > commitment_start: return False

        if _is_slot_globally_taken(current_slot_time, exam_id): return False
        
        current_slot_time += EXAM_DURATION
            
    return True

def _schedule_exams_in_db(patient_id: int, ordered_exam_ids: list[int], start_time: datetime) -> None:
    try:
        current_time_for_scheduling = start_time
        for exam_id in ordered_exam_ids:
            new_exam = ScheduledExam(
                patient_id=patient_id, 
                exam_id=exam_id, 
                date=current_time_for_scheduling,
            )
            db.session.add(new_exam)
            current_time_for_scheduling += EXAM_DURATION
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise

def find_and_schedule_optimized_exams(patient_id: int, exam_names: list[str]) -> dict | None:
    exam_objects = db.session.query(Exam).filter(Exam.type.in_(exam_names)).all()
    if len(exam_objects) != len(exam_names): raise ValueError("Um ou mais tipos de exame não foram encontrados.")

    exam_id_map = {exam.type: exam.id for exam in exam_objects}
    exam_ids_in_order = [exam_id_map[name] for name in exam_names]
    
    target_date = date.today() + timedelta(days=1)
    
    all_permutations = list(itertools.permutations(exam_ids_in_order))

    for permuted_ids in all_permutations:
        first_exam_id = permuted_ids[0]
        possible_start_slots = _fetch_exam_availability_or_default(target_date, first_exam_id)
        
        for block_start in possible_start_slots:
            if _check_block_viability(block_start, permuted_ids, patient_id):
                _schedule_exams_in_db(patient_id, permuted_ids, block_start)
                
                scheduled_exam_names = [next(e.type for e in exam_objects if e.id == eid) for eid in permuted_ids]
                return {
                    "scheduled_order": scheduled_exam_names,
                    "start_time": block_start.isoformat()
                }
                
    return None

def schedule_exams_at_specific_time(patient_id: int, exam_names: list[str], desired_start_str: str) -> dict | None:
    try:
        desired_start_time = datetime.fromisoformat(desired_start_str)
    except ValueError:
        raise ValueError("Formato de data/hora inválido. Use o formato ISO (YYYY-MM-DDTHH:MM:SS).")

    exam_objects = db.session.query(Exam).filter(Exam.type.in_(exam_names)).all()
    if len(exam_objects) != len(exam_names): raise ValueError("Um ou mais tipos de exame não foram encontrados.")

    exam_id_map = {exam.type: exam.id for exam in exam_objects}
    exam_ids_in_order = [exam_id_map[name] for name in exam_names]

    all_permutations = list(itertools.permutations(exam_ids_in_order))

    for permuted_ids in all_permutations:
        if _check_block_viability(desired_start_time, permuted_ids, patient_id):
            _schedule_exams_in_db(patient_id, permuted_ids, desired_start_time)
            
            scheduled_exam_names = [next(e.type for e in exam_objects if e.id == eid) for eid in permuted_ids]
            return {
                "scheduled_order": scheduled_exam_names,
                "start_time": desired_start_time.isoformat()
            }
            
    return None

def suggest_optimized_schedule(patient_id: int, exam_names: list[str], start_search_date: date) -> dict | None:
    exam_objects = db.session.query(Exam).filter(Exam.type.in_(exam_names)).all()
    if len(exam_objects) != len(exam_names):
        raise ValueError("Um ou mais tipos de exame não foram encontrados.")

    exam_id_map = {exam.type: exam.id for exam in exam_objects}
    exam_ids_in_order = [exam_id_map[name] for name in exam_names]
    
    for i in range(30): # Procura por horários nos próximos 30 dias
        target_date = start_search_date + timedelta(days=i)
        all_permutations = list(itertools.permutations(exam_ids_in_order))

        for permuted_ids in all_permutations:
            first_exam_id = permuted_ids[0]
            possible_start_slots = _fetch_exam_availability_or_default(target_date, first_exam_id)
            
            for block_start in possible_start_slots:
                if _check_block_viability(block_start, permuted_ids, patient_id):
                    scheduled_exam_names = [next(e.type for e in exam_objects if e.id == eid) for eid in permuted_ids]
                    
                    agendamentos_detalhados = []
                    current_time = block_start
                    for exam_name in scheduled_exam_names:
                        agendamentos_detalhados.append({
                            "exame": exam_name,
                            "horario": current_time.isoformat()
                        })
                        current_time += EXAM_DURATION

                    return {
                        "sugestao_agendamento": agendamentos_detalhados
                    }
                    
    return None

def get_all_available_slots_for_exams(exam_names: list[str], target_date: date) -> dict:
    exam_objects = db.session.query(Exam).filter(Exam.type.in_(exam_names)).all()
    if len(exam_objects) != len(exam_names):
        raise ValueError("Um ou mais tipos de exame não foram encontrados.")

    all_slots = {}
    for exam in exam_objects:
        exam_day_slots = _fetch_exam_availability_or_default(target_date, exam.id)
        
        free_slots = []
        for slot_time in exam_day_slots:
            if not _is_slot_globally_taken(slot_time, exam.id):
                free_slots.append(slot_time.isoformat())
        
        all_slots[exam.type] = free_slots

    return all_slots