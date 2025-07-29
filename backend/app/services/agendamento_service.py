
from datetime import datetime, time, timedelta
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload
from .. import db
from ..models import Doctor, Patient, DoctorAvailability, Appointment, Specialty

def buscar_horarios_disponiveis_db(info_pedido):
    especialidades = info_pedido.get("especialistas")
    if not especialidades or not isinstance(especialidades, list):
        return []

    # Busca médicos que tenham qualquer das especialidades informadas
    doctors = db.session.query(Doctor).join(Doctor.specialties).filter(
        or_(*[Specialty.name.ilike(f"%{esp.strip()}%") for esp in especialidades])
    ).options(joinedload(Doctor.specialties)).all()

    if not doctors:
        return []

    doctor_ids = [doctor.id for doctor in doctors]

    avail_query = db.session.query(DoctorAvailability).filter(
        DoctorAvailability.doctor_id.in_(doctor_ids)
    )

    data_desejada = None
    data_desejada_str = info_pedido.get("data_base")
    if data_desejada_str:
        try:
            data_desejada = datetime.strptime(data_desejada_str, "%Y-%m-%d").date()
            avail_query = avail_query.filter(db.func.date(DoctorAvailability.date) == data_desejada)
        except (ValueError, TypeError):
            pass

    periodo_dia = info_pedido.get("periodo_dia")
    if periodo_dia and data_desejada:
        if periodo_dia == "manha":
            inicio = datetime.combine(data_desejada, time(6, 0))
            fim = datetime.combine(data_desejada, time(11, 59, 59))
        elif periodo_dia == "tarde":
            inicio = datetime.combine(data_desejada, time(12, 0))
            fim = datetime.combine(data_desejada, time(17, 59, 59))
        elif periodo_dia == "noite":
            inicio = datetime.combine(data_desejada, time(18, 0))
            fim = datetime.combine(data_desejada, time(23, 59, 59))
        else:
            inicio = None
            fim = None

        if inicio and fim:
            avail_query = avail_query.filter(DoctorAvailability.date.between(inicio, fim))

    availabilities = avail_query.options(joinedload(DoctorAvailability.doctor).joinedload(Doctor.specialties)).all()
    if not availabilities:
        return []

    horarios_ocupados_query = db.session.query(Appointment.date).filter(
        Appointment.date.in_([av.date for av in availabilities])
    )
    horarios_ocupados = [h[0] for h in horarios_ocupados_query.all()]

    horarios_disponiveis = []
    for availability in availabilities:
        if availability.date not in horarios_ocupados:
            doctor = availability.doctor
            especialidades_nomes = ", ".join([esp.name.capitalize() for esp in doctor.specialties])
            horarios_disponiveis.append({
                "especialista": especialidades_nomes,
                "medico_id": doctor.id,
                "medico_nome": doctor.name,
                "horario": availability.date.strftime("%Y-%m-%d %H:%M")
            })

    horarios_disponiveis.sort(key=lambda x: (x['especialista'], x['horario']))
    return horarios_disponiveis


def confirmar_agendamento_db(email, cpf, agendamentos):
    paciente = db.session.query(Patient).filter(or_(Patient.email == email, Patient.cpf == cpf)).first()
    if not paciente:
        nome_paciente = email.split('@')[0]
        paciente = Patient(name=nome_paciente, email=email, cpf=cpf)
        db.session.add(paciente)
        db.session.flush()

    agendamentos_confirmados = []
    erros = []

    for agendamento in agendamentos:
        medico_id = agendamento.get('medico_id')
        horario_str = agendamento.get('horario')
        horario_dt = datetime.strptime(horario_str, "%Y-%m-%d %H:%M")
        
        disponibilidade = db.session.query(DoctorAvailability).filter_by(doctor_id=medico_id, date=horario_dt).first()
        agendamento_existente = db.session.query(Appointment).filter_by(date=horario_dt, doctor_id=medico_id).first()
        
        if not disponibilidade or agendamento_existente:
            erros.append(f"O horário {horario_str} para o médico ID {medico_id} não está mais disponível.")
            continue
        
        novo_agendamento = Appointment(
            doctor_id=medico_id,
            patient_id=paciente.id,
            date=horario_dt,
            status='Scheduled'
        )
        db.session.add(novo_agendamento)
        
        db.session.delete(disponibilidade)
        
        agendamentos_confirmados.append(novo_agendamento)

    if erros:
        db.session.rollback()
        return None, erros
        
    db.session.commit()
    return agendamentos_confirmados, None

def encontrar_proximo_dia_disponivel(especialistas, data_base_str, periodo_dia):
    data_atual = datetime.strptime(data_base_str, "%Y-%m-%d").date()
    max_dias_busca = 30 

    for i in range(1, max_dias_busca + 1):
        proxima_data = data_atual + timedelta(days=i)
        info_pedido = {
            "especialistas": especialistas,
            "data_base": proxima_data.strftime("%Y-%m-%d"),
            "periodo_dia": periodo_dia
        }
        horarios = buscar_horarios_disponiveis_db(info_pedido)
        if horarios:
            return {
                "pedido_entendido": info_pedido,
                "horarios_encontrados": horarios
            }
    return None

def encontrar_proximo_dia_disponivel(especialistas, data_base_str, periodo_dia):
    data_atual = datetime.strptime(data_base_str, "%Y-%m-%d").date()
    max_dias_busca = 30 

    for i in range(1, max_dias_busca + 1):
        proxima_data = data_atual + timedelta(days=i)
        info_pedido = {
            "especialistas": especialistas,
            "data_base": proxima_data.strftime("%Y-%m-%d"),
            "periodo_dia": periodo_dia
        }
        horarios = buscar_horarios_disponiveis_db(info_pedido)
        if horarios:
            return {
                "pedido_entendido": info_pedido,
                "horarios_encontrados": horarios
            }
    return None