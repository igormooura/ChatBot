# backend/app/router/user_routes.py
from flask import Blueprint, request, jsonify
from ..services.User_Service import register_user, authenticate_user

bp = Blueprint('user_api', __name__, url_prefix='/user')

@bp.route('/register', methods=['POST'])
def register():
    """
    Endpoint para registrar um novo usuário.
    Espera um JSON com: username, email, password, patient_name, patient_cpf
    """
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Corpo da requisição não pode ser vazio."}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    patient_name = data.get('patient_name') # Nome completo para o perfil de paciente
    patient_cpf = data.get('patient_cpf')   # CPF para o perfil de paciente

    required_fields = [username, email, password, patient_name, patient_cpf]
    if not all(required_fields):
        return jsonify({"erro": "Todos os campos são obrigatórios: username, email, password, patient_name, patient_cpf."}), 400

    user, message = register_user(username, email, password, patient_name, patient_cpf)

    if not user:
        return jsonify({"erro": message}), 409 # Conflict

    return jsonify({
        "mensagem": message,
        "user": {"id": user.id, "username": user.username, "email": user.email}
    }), 201

@bp.route('/login', methods=['POST'])
def login():
    """
    Endpoint para login de usuário.
    Espera um JSON com: email, password
    """
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Corpo da requisição não pode ser vazio."}), 400
        
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({"erro": "E-mail e senha são obrigatórios."}), 400

    user, message = authenticate_user(email, password)

    if not user:
        return jsonify({"erro": message}), 401 # Unauthorized

    return jsonify({
        "mensagem": message,
        "user": {"id": user.id, "username": user.username, "email": user.email, "patient_id": user.patient.id}
    })