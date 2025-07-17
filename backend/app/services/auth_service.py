# backend/app/services/auth_service.py
import jwt
from datetime import datetime, timedelta, timezone
from flask import current_app
from .. import db
from ..models import Patient, AuthToken

def create_patient(name, cpf, email):
    if Patient.query.filter((Patient.cpf == cpf) | (Patient.email == email)).first():
        return None, "CPF ou E-mail já registado."
    
    new_patient = Patient(name=name, cpf=cpf, email=email)
    db.session.add(new_patient)
    db.session.commit()
    return new_patient, "Paciente registado com sucesso."

def request_login_token(email, cpf):
    patient = Patient.query.filter_by(email=email, cpf=cpf).first()
    if not patient:
        return None, "Credenciais inválidas. Verifique o seu e-mail e CPF."
    
    AuthToken.query.filter_by(patient_id=patient.id).delete()

    new_token = AuthToken(patient_id=patient.id)
    db.session.add(new_token)
    db.session.commit()
    
    print(f"DEBUG: Token para {email}: {new_token.token}") 
    return new_token.token, "Um token de acesso foi enviado para o seu e-mail."

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
