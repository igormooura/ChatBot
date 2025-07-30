# backend/app/utils/decorators.py
import jwt
from functools import wraps
from flask import request, jsonify, current_app
from ..models import Patient

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Se for preflight OPTIONS, não barrar
        if request.method == 'OPTIONS':
            return jsonify({'message': 'OK'}), 200

        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Formato do token inválido. Use "Bearer <token>".'}), 401

        if not token:
            return jsonify({'message': 'Token de autenticação em falta.'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = Patient.query.get(data['sub'])

            if not current_user:
                return jsonify({'message': 'Utilizador do token não encontrado.'}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado. Por favor, faça login novamente.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido.'}), 401

        return f(current_user, *args, **kwargs)

    return decorated
