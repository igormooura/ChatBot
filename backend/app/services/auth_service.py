# backend/app/services/auth_service.py
from .. import db
from ..models import Patient, AuthToken

def create_patient(name, cpf, email):
    """Cria um novo paciente se o CPF ou E-mail não existirem."""
    if Patient.query.filter((Patient.cpf == cpf) | (Patient.email == email)).first():
        return None, "CPF ou E-mail já registado."
    
    new_patient = Patient(name=name, cpf=cpf, email=email)
    db.session.add(new_patient)
    db.session.commit()
    return new_patient, "Paciente registado com sucesso."

def request_login_token(email, cpf):
    """
    Verifica as credenciais e, se válidas, gera e 'envia' um token de login.
    """
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
    """Verifica um token. Se for válido, retorna os dados do paciente e apaga o token."""
    token = AuthToken.query.filter_by(token=token_str).first()

    if not token or token.is_expired():
        return None, "Token inválido ou expirado."

    patient = token.patient
    
    # O token é de uso único, então apagamo-lo após a verificação
    db.session.delete(token)
    db.session.commit()
    
    return patient, "Login bem-sucedido."