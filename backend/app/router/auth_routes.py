from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from ..services.auth_service import create_patient, request_login_token, verify_login_token
from ..utils.decorators import token_required

bp = Blueprint('auth_api', __name__, url_prefix='/')


@bp.route('/register', methods=['POST'])
@cross_origin()
def register():

    """Endpoint para registrar um novo paciente."""
    data = request.get_json()
    if not all(k in data for k in ['name', 'cpf', 'email']):
        return jsonify({"erro": "Campos 'name', 'cpf' e 'email' são obrigatórios."}), 400

    patient, message = create_patient(data['name'], data['cpf'], data['email'])
    
    if not patient:
        return jsonify({"erro": message}), 409  
    
    return jsonify({"mensagem": message, "patient_id": patient.id}), 201


@bp.route('/auth/request-token', methods=['POST'])
@cross_origin()
def handle_request_token():

    data = request.get_json()
    if not all(k in data for k in ['email', 'cpf']):
        return jsonify({"erro": "Campos 'email' e 'cpf' são obrigatórios."}), 400
    
    token, message = request_login_token(data['email'], data['cpf'])
    
    if not token:
        return jsonify({"erro": message}), 401  
    
    return jsonify({"mensagem": message, "debug_token": token}), 200


@bp.route('/auth/verify-token', methods=['POST'])
@cross_origin()
def handle_verify_token():
    data = request.get_json()
    if 'token' not in data:
        return jsonify({"erro": "O campo 'token' é obrigatório."}), 400

    jwt_token, message = verify_login_token(data['token'])

    if not jwt_token:
        return jsonify({"erro": message}), 401  

    return jsonify({
        "mensagem": message,
        "jwt_token": jwt_token["token"],
        "cpf": jwt_token["cpf"]
    })


