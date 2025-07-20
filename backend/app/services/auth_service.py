# backend/app/services/auth_service.py

from flask import current_app
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import jwt 
from datetime import datetime, timedelta, timezone

from .. import db
from ..models import Patient
from .email_service import send_email 

def create_patient(name, cpf, email):
    """
    Cria um novo paciente no banco de dados, garantindo que o CPF seja salvo sem pontuação.
    """
    cpf_limpo = "".join(filter(str.isdigit, cpf))

    paciente_existente = Patient.query.filter(
        (Patient.cpf == cpf_limpo) | (Patient.email == email)
    ).first()

    if paciente_existente:
        return None, "CPF ou E-mail já registado."

    # Cria e salva o novo paciente com o CPF limpo
    novo_paciente = Patient(name=name, cpf=cpf_limpo, email=email)
    db.session.add(novo_paciente)
    db.session.commit()
    
    return novo_paciente, "Paciente registrado com sucesso."


def request_login_token(email, cpf):
    """
    Verifica o paciente, gera um token de uso único e o envia por e-mail.
    """
    cpf_limpo = "".join(filter(str.isdigit, cpf))
    patient = Patient.query.filter_by(cpf=cpf_limpo).first()

    if not patient:
        return None, "CPF não encontrado."
    
    if patient.email != email:
        return None, "O e-mail não corresponde ao CPF informado."

    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    one_time_token = serializer.dumps(patient.email, salt='login-token')

    html_body = f"""
        <h1>Seu Código de Acesso</h1>
        <p>Use o código abaixo para fazer login no sistema.</p>
        <p>Este código é válido por 10 minutos.</p>
        <h2 style="font-size: 1.5em; letter-spacing: 3px; text-align: center; background-color: #f0f0f0; padding: 10px; border-radius: 5px;">
            <strong>{one_time_token}</strong>
        </h2>
    """

    try:
        send_email(to=patient.email, subject="Seu Código de Acesso", template=html_body)
        return one_time_token, "Token enviado para o seu e-mail."
    except Exception as e:
        current_app.logger.error(f"Falha ao enviar e-mail: {e}")
        return None, "Erro ao enviar o e-mail."


def verify_login_token(token):
    """
    Verifica o token de uso único. Se for válido, retorna um token JWT de sessão.
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='login-token', max_age=600) # 600 segundos = 10 minutos
    except SignatureExpired:
        return None, "Token expirado. Por favor, solicite um novo."
    except Exception:
        return None, "Token inválido."

    # Se o token é válido, busca o paciente pelo e-mail contido no token
    patient = Patient.query.filter_by(email=email).first()
    if not patient:
        return None, "Usuário do token não encontrado."

    payload = {
        'iat': datetime.now(timezone.utc), # Issued at
        'exp': datetime.now(timezone.utc) + timedelta(hours=8), # Expiration time
        'sub': patient.id, # Subject (o ID do usuário)
    }
    jwt_token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    
    return jwt_token, "Login realizado com sucesso."