# backend/app/services/agendamento_service.py

from datetime import datetime, time
from sqlalchemy import and_
from .. import db
from ..models import Doctor, Patient, DoctorAvailability, Appointment

def buscar_horarios_disponiveis_db(info_pedido):
    """
    Busca horários disponíveis no banco de dados com base nos critérios.
    Critérios: especialista, data_base, periodo_dia.
    """
    especialidade = info_pedido.get("especialista")
    if not especialidade:
        return []

    query = db.session.query(Doctor).filter(Doctor.specialty.ilike(f'%{especialidade}%'))
    
    doctors = query.all()
    if not doctors:
        return []

    doctor_ids = [doctor.id for doctor in doctors]

    avail_query = db.session.query(DoctorAvailability).filter(DoctorAvailability.doctor_id.in_(doctor_ids))


    data_desejada_str = info_pedido.get("data_base")
    if data_desejada_str:
        data_desejada = datetime.strptime(data_desejada_str, "%Y-%m-%d").date()
        avail_query = avail_query.filter(db.func.date(DoctorAvailability.date) == data_desejada)

    periodo_dia = info_pedido.get("periodo_dia")
    if periodo_dia:
        if periodo_dia == "manha":
            avail_query = avail_query.filter(and_(db.func.cast(DoctorAvailability.date, db.Time) >= time(0, 0), db.func.cast(DoctorAvailability.date, db.Time) < time(12, 0)))
        elif periodo_dia == "tarde":
            avail_query = avail_query.filter(and_(db.func.cast(DoctorAvailability.date, db.Time) >= time(12, 0), db.func.cast(DoctorAvailability.date, db.Time) < time(18, 0)))
        elif periodo_dia == "noite":
            avail_query = avail_query.filter(and_(db.func.cast(DoctorAvailability.date, db.Time) >= time(18, 0), db.func.cast(DoctorAvailability.date, db.Time) <= time(23, 59)))

    availabilities = avail_query.all()

    horarios_ocupados = [
        app.date for app in db.session.query(Appointment).filter(Appointment.date.in_([av.date for av in availabilities])).all()
    ]


    horarios_disponiveis = []
    for DoctorAvailability in availabilities:
        if DoctorAvailability.date not in horarios_ocupados:
            horarios_disponiveis.append({
                "especialista": DoctorAvailability.doctor.specialty.capitalize(),
                "medico_id": DoctorAvailability.doctor.id,
                "medico_nome": DoctorAvailability.doctor.name,
                "horario": DoctorAvailability.date.strftime("%Y-%m-%d %H:%M")
            })

    horarios_disponiveis.sort(key=lambda x: x['horario'])
    return horarios_disponiveis


def confirmar_agendamento_db(nome_paciente, medico_id, horario_str):
    """
    Registra uma nova consulta (Appointment) no banco de dados.
    """
    horario_dt = datetime.strptime(horario_str, "%Y-%m-%d %H:%M")


    disponibilidade = db.session.query(DoctorAvailability).filter_by(doctor_id=medico_id, date=horario_dt).first()
    agendamento_existente = db.session.query(Appointment).filter_by(doctor_id=medico_id, date=horario_dt).first()

    if not disponibilidade or agendamento_existente:
        return None 


    paciente = db.session.query(Patient).filter_by(name=nome_paciente).first()
    if not paciente:
        cpf_ficticio = f"000.000.{datetime.now().microsecond:06d}"
        paciente = Patient(name=nome_paciente, cpf=cpf_ficticio)
        db.session.add(paciente)
        db.session.flush()


    novo_agendamento = Appointment(
        doctor_id=medico_id,
        patient_id=paciente.id,
        date=horario_dt,
        status='Scheduled' 
    )
    db.session.add(novo_agendamento)
    db.session.commit()

    return novo_agendamento