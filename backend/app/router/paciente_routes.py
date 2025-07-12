from flask import Blueprint, request, jsonify
from ..services.paciente_service import get_patient_by_id, update_patient_profile

bp = Blueprint('paciente_api', __name__, url_prefix='/paciente')

@bp.route('/<int:patient_id>', methods=['GET'])
def get_meu_perfil(patient_id):
    """
    Busca o perfil do paciente logado.
    O frontend envia o ID do paciente que obteve no login.
    """
    # ID do paciente de um token de autenticação (JWT) para garantir que o utilizador só possa ver o seu próprio perfil.
    
    patient = get_patient_by_id(patient_id)

    if not patient:
        return jsonify({"erro": "Perfil de paciente não encontrado."}), 404

    return jsonify({
        "id": patient.id,
        "nome": patient.name,
        "cpf": patient.cpf,
        "user_id": patient.user_id
    })

@bp.route('/<int:patient_id>', methods=['PUT'])
def update_meu_perfil(patient_id):
    """
    Atualiza o perfil do paciente logado.
    """
    
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Corpo da requisição não pode ser vazio."}), 400

    patient, message = update_patient_profile(patient_id, data)

    if not patient:
        return jsonify({"erro": message}), 404
        
    return jsonify({"mensagem": message})