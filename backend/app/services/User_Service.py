# backend/app/services/user_service.py
from .. import db
from ..models import User, Patient

def register_user(username, email, password, patient_name, patient_cpf):
    """
    Registra um novo usuário e seu perfil de paciente associado.
    Verifica se o username ou email já existem.
    """
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return None, "Nome de usuário ou e-mail já existente."
        
    if Patient.query.filter_by(cpf=patient_cpf).first():
        return None, "CPF já cadastrado."

    # Cria o paciente primeiro
    new_patient = Patient(name=patient_name, cpf=patient_cpf)

    # Cria o usuário e associa ao paciente
    new_user = User(username=username, email=email, patient=new_patient)
    new_user.set_password(password)

    db.session.add(new_user) # O paciente é adicionado em cascata
    db.session.commit()
    
    return new_user, "Usuário registrado com sucesso."

def authenticate_user(email, password):
    """
    Autentica um usuário pelo email e senha.
    Retorna o usuário se as credenciais forem válidas.
    """
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        return user, "Login bem-sucedido."
    
    return None, "E-mail ou senha inválidos."