# backend/app/services/auth_service.py

from flask import current_app
from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import SQLAlchemyError
import jwt # Import the jwt library

from .. import db
from ..models import Patient, AuthToken # Ensure AuthToken and Patient are imported
from .email_service import send_email # Assuming this service exists


# --- JWT Helper Functions ---
def generate_jwt_token(patient_id):
    """
    Generates a JWT token for a given patient ID.
    The token includes patient_id and an expiration time.
    """
    try:
        payload = {
            'patient_id': patient_id,
            'exp': datetime.now(timezone.utc) + timedelta(hours=24) # Token valid for 24 hours
        }
        # Use the secret key from current_app.config
        # PyJWT 2.x+ returns str, older versions might return bytes.
        # We'll ensure it's a string before returning.
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        return token
    except Exception as e:
        current_app.logger.error(f"Error generating JWT: {e}")
        return None

def verify_jwt_token(token):
    """
    Decodes and verifies a JWT token.
    Returns the decoded payload if valid, None otherwise.
    This function will be used by decorators for protected routes.
    """
    try:
        # Use the secret key from current_app.config
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        current_app.logger.warning("JWT expired.")
        return None
    except jwt.InvalidTokenError:
        current_app.logger.warning("Invalid JWT.")
        return None
    except Exception as e:
        current_app.logger.error(f"Error verifying JWT: {e}")
        return None

# --- Existing Functions (with minor improvements for robustness) ---

def create_patient(name, cpf, email):
    cpf_limpo = "".join(filter(str.isdigit, cpf))

    # Convert email to lowercase for case-insensitive check
    email_lower = email.lower()

    paciente_existente = Patient.query.filter(
        (Patient.cpf == cpf_limpo) | (Patient.email == email_lower) # Check against lowercased email
    ).first()

    if paciente_existente:
        return None, "CPF ou E-mail já registrado."

    try:
        novo_paciente = Patient(name=name, cpf=cpf_limpo, email=email_lower) # Store lowercased email
        db.session.add(novo_paciente)
        db.session.commit()
        return novo_paciente, "Paciente registrado com sucesso."
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Erro ao registrar paciente.")
        return None, "Erro ao registrar paciente."


def request_login_token(email, cpf):
    cpf_limpo = "".join(filter(str.isdigit, cpf))
    email_lower = email.lower() # Convert input email to lowercase

    patient = Patient.query.filter_by(cpf=cpf_limpo).first()

    if not patient:
        return None, "CPF não encontrado."

    # Compare stored email (already lowercased if following create_patient) with lowercased input email
    if patient.email != email_lower:
        return None, "O e-mail não corresponde ao CPF informado."

    try:
        # Optional: Delete any existing unverified tokens for this patient
        # This prevents a user from having multiple active one-time tokens
        AuthToken.query.filter_by(patient_id=patient.id).delete()
        db.session.commit()

        auth_token = AuthToken(patient_id=patient.id)
        db.session.add(auth_token)
        db.session.commit()

        one_time_token = auth_token.token

        current_app.logger.debug(f"Token gerado: {one_time_token}")
        print("DEBUG TOKEN:", one_time_token) # Consider removing or changing this in production

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception(f"Erro ao gerar ou salvar token único: {e}")
        return None, f"Erro ao gerar token: {str(e)}"

    html_body = f"""
        <h1>Seu Código de Acesso</h1>
        <p>Use o código abaixo para fazer login no sistema.</p>
        <p>Este código é válido por 10 minutos.</p>
        <div style="font-size: 1.5em; letter-spacing: 3px; text-align: center;
                    background-color: #f0f0f0; padding: 10px; border-radius: 5px;">
            <strong>{one_time_token}</strong>
        </div>
    """

    try:
        send_email(to=patient.email, subject="Seu Código de Acesso", template=html_body)
        # In production, you might return only a success message, not the token itself.
        return one_time_token, "Token enviado para o seu e-mail."
    except Exception as e:
        current_app.logger.error(f"Falha ao enviar e-mail: {e}")
        # Decide if you want to rollback the token creation if email fails.
        # For now, it keeps the token, allowing retry.
        return None, "Erro ao enviar o e-mail."


def verify_login_token(token_str):
    if not token_str or not token_str.strip():
        return None, "Token vazio ou ausente."

    token = AuthToken.query.filter_by(token=token_str).first()
    if not token:
        current_app.logger.warning("Token inválido ou não encontrado.")
        return None, "Token inválido."

    if token.is_expired():
        current_app.logger.info(f"Token expirado para o paciente ID {token.patient_id}")
        # Clean up the expired token immediately
        try:
            db.session.delete(token)
            db.session.commit()
        except Exception:
            current_app.logger.exception("Erro ao excluir token expirado após verificação.")
        return None, "Token expirado."

    patient = token.patient
    if not patient:
        current_app.logger.error(f"Token encontrado, mas paciente inexistente (ID {token.patient_id})")
        return None, "Paciente não encontrado para este token."

    try:
        db.session.delete(token) # Delete the one-time token after successful verification
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Erro ao excluir token após autenticação bem-sucedida.")
        return None, "Erro ao processar o token. Tente novamente."

    # --- JWT Implementation Starts Here ---
    jwt_token = generate_jwt_token(patient.id)
    if not jwt_token:
        current_app.logger.error(f"Falha ao gerar JWT para paciente ID {patient.id}.")
        return None, "Erro interno ao gerar token de sessão."

    # Ensure the JWT token is a string, especially if using PyJWT < 2.0
    if isinstance(jwt_token, bytes):
        jwt_token = jwt_token.decode('utf-8')

    return {
        "access_token": jwt_token,
        "patient_email": patient.email,
        "message": "Autenticação bem-sucedida. Use o access_token para futuras requisições."
    }, "Autenticação bem-sucedida."