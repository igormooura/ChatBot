from .. import db
from ..models import Patient

def get_patient_by_id(patient_id):
    """Busca um paciente pelo seu ID."""
    return Patient.query.get(patient_id)

def update_patient_profile(patient_id, data):
    """
    Atualiza os dados de um paciente.
    'data' é um dicionário com os campos a serem atualizados (ex: {'name': 'Novo Nome'}).
    """
    patient = get_patient_by_id(patient_id)
    if not patient:
        return None, "Paciente não encontrado."

    if 'name' in data:
        patient.name = data['name']
    if 'cpf' in data:
        patient.cpf = data['cpf']
    
    db.session.commit()
    return patient, "Perfil atualizado com sucesso."