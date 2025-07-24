# backend/app/services/auth_service.py

from flask import current_app
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import jwt 
from datetime import datetime, timedelta, timezone

from .. import db
from ..models import Patient
from .email_service import send_email 

def create_patient(name, cpf, email):
   
    cpf_limpo = "".join(filter(str.isdigit, cpf))

    paciente_existente = Patient.query.filter(
        (Patient.cpf == cpf_limpo) | (Patient.email == email)
    ).first()

    if paciente_existente:
        return None, "CPF ou E-mail ja registado."

    # Cria e salva o novo paciente com o CPF limpo
    novo_paciente = Patient(name=name, cpf=cpf_limpo, email=email)
    db.session.add(novo_paciente)
    
    db.session.commit()
    
    return novo_paciente, "Paciente registrado com sucesso."


def request_login_token(email, cpf):
    cpf_limpo = "".join(filter(str.isdigit, cpf))
    patient = Patient.query.filter_by(cpf=cpf_limpo).first()

    if not patient:
        return None, "CPF nao encontrado."
    
    if patient.email != email:
        return None, "O e-mail nao corresponde ao CPF informado."

    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    one_time_token = serializer.dumps(patient.email, salt='login-token')

    html_body = f"""
        <h1>Seu Codigo de Acesso</h1>
        <p>Use o codigo abaixo para fazer login no sistema.</p>
        <p>Este ccdigo e valido por 10 minutos.</p>
        <h2 style="font-size: 1.5em; letter-spacing: 3px; text-align: center; background-color: #f0f0f0; padding: 10px; border-radius: 5px;">
            <strong>{one_time_token}</strong>
        </h2>
    """

    try:
        send_email(to=patient.email, subject="Seu Codigo de Acesso", template=html_body)
        return one_time_token, "Token enviado para o seu e-mail."
    except Exception as e:
        current_app.logger.error(f"Falha ao enviar e-mail: {e}")
        return None, "Erro ao enviar o e-mail."

def verify_login_token(token_str):
    try:
        token = AuthToken.query.filter_by(token=token_str).first()
        if not token:
            print("DEBUG - Token não encontrado.")
            return None, "Token inválido."

        if token.is_expired():
            print("DEBUG - Token expirado.")
            return None, "Token expirado."

        patient = token.patient

        db.session.delete(token)
        db.session.commit()

        secret = current_app.config.get('SECRET_KEY')
        if not secret:
            print("ERRO - SECRET_KEY não está definido!")
            return None, "Erro interno de autenticação."

        jwt_payload = {
            'exp': datetime.now(timezone.utc) + timedelta(hours=24),
            'iat': datetime.now(timezone.utc),
            'sub': patient.id
        }

        jwt_token = jwt.encode(jwt_payload, secret, algorithm='HS256')

        return {
            "token": jwt_token,
            "email": patient.email
        }, "Autenticação bem-sucedida."
    
    except Exception as e:
        print("ERRO INTERNO no verify_login_token:", str(e))
        return None, "Erro interno ao verificar o token."

