from flask import Blueprint, jsonify
from app.models.Appointment import Appointment
from app.models.Patient import Patient
from app import db

consultas_usuarios_bp = Blueprint('consultas_usuarios', __name__)

@consultas_usuarios_bp.route('/consultas/<cpf>', methods=['GET'])
def get_consultas_por_cpf(cpf):
    paciente = db.session.query(Patient).filter_by(cpf=cpf).first()
    if not paciente:
        return jsonify({"erro": "Paciente não encontrado."}), 404

    consultas = db.session.query(Appointment).filter_by(patient_id=paciente.id).all()

    return jsonify([
        {
            "id": consulta.id,
            "data": consulta.date.isoformat(),
            "status": consulta.status,
            "medico": consulta.doctor.name
        }
        for consulta in consultas
    ]), 200

@consultas_usuarios_bp.route('/todas-consultas', methods=['GET'])
def get_todas_consultas():
    consultas = db.session.query(Appointment).all()

    return jsonify([
        {
            "id": consulta.id,
            "data": consulta.date.isoformat(),
            "status": consulta.status,
            "paciente": consulta.patient.name,
            "cpf_paciente": consulta.patient.cpf,
            "medico": consulta.doctor.name
        }
        for consulta in consultas
    ]), 200
