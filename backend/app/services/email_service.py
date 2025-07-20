# backend/app/services/email_service.py

from flask_mail import Message
from .. import mail
from flask import current_app, render_template
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config.get('SECURITY_PASSWORD_SALT', 'my_precious'))

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config.get('SECURITY_PASSWORD_SALT', 'my_precious'),
            max_age=expiration
        )
    except SignatureExpired:
        return None  # Token expirado
    except Exception:
        return None  # Token inválido
    return email

def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)

def send_registration_token(user_email):
    """
    Gera um token e envia o e-mail de confirmação.
    """
    token = generate_confirmation_token(user_email)
    

    html_body = f"""
    <h1>Bem-vindo ao nosso sistema!</h1>
    <p>Obrigado por se registrar. Por favor, use o token a seguir para ativar sua conta:</p>
    <h2><strong>{token}</strong></h2>
    <p>Este token é válido por 1 hora.</p>
    """
    
    send_email(user_email, "Confirmação de Cadastro", html_body)