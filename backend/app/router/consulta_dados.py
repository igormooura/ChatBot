from flask import Blueprint, jsonify
from app.models.Appointment import Appointment
from app.models.Patient import Patient
from app.models.ScheculedExam import ScheduledExam
from ..utils.decorators import token_required
from app import db
from flask_cors import cross_origin

consultas_usuarios_bp = Blueprint('consultas_dados', __name__)


@consultas_usuarios_bp.route('/consultas/<cpf>', methods=['GET', 'OPTIONS'])
@token_required
@cross_origin()
def get_consultas_por_cpf(current_user, cpf):   # <-- agora espera current_user
    paciente = db.session.query(Patient).filter_by(cpf=cpf).first()
    if not paciente:
        return jsonify({"erro": "Paciente não encontrado."}), 404

    consultas = db.session.query(Appointment).filter_by(patient_id=paciente.id).all()
    exames = db.session.query(ScheduledExam).filter_by(patient_id=paciente.id).all()

    return jsonify({
        "consultas": [
            {
                "id": consulta.id,
                "tipo": "consulta",
                "data": consulta.date.isoformat(),
                "status": consulta.status,
                "medico": consulta.doctor.name
            }
            for consulta in consultas
        ],
        "exames": [
            {
                "id": exame.id,
                "tipo": "exame",
                "data": exame.date.isoformat(),
                "status": exame.status,
                "exame": exame.exam.type
            }
            for exame in exames
        ]
    }), 200



@consultas_usuarios_bp.route('/todas-consultas', methods=['GET'])
@cross_origin()
def get_todas_consultas():
    consultas = db.session.query(Appointment).all()
    exames = db.session.query(ScheduledExam).all()

    return jsonify({
        "consultas": [
            {
                "id": consulta.id,
                "tipo": "consulta",
                "data": consulta.date.isoformat(),
                "status": consulta.status,
                "cpf": consulta.patient.cpf,
                "medico": consulta.doctor.name
            }
            for consulta in consultas
        ],
        "exames": [
            {
                "id": exame.id,
                "tipo": "exame",
                "data": exame.date.isoformat(),
                "status": exame.status,
                "cpf": exame.patient.cpf,
                "exame": exame.exam.type
            }
            for exame in exames
        ]
    }), 200
