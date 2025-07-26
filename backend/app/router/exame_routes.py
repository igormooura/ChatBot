from flask import Blueprint, request, jsonify
from datetime import datetime, date

from ..services.exame_service import (
    suggest_optimized_schedule,
    get_all_available_slots_for_exams,
    schedule_exams_at_specific_time
)

bp = Blueprint('exames', __name__, url_prefix='/api/exames')

@bp.route('/sugerir-horario-otimizado', methods=['POST'])
def handle_sugestao_otimizada():
    data = request.get_json()
    patient_id = data.get('patient_id')
    exam_names = data.get('exam_names')
    data_inicio_str = data.get('data_inicio')

    if not all([patient_id, exam_names, data_inicio_str]):
        return jsonify({"erro": "patient_id, exam_names e data_inicio são obrigatórios."}), 400
    
    try:
        start_date = datetime.strptime(data_inicio_str, "%Y-%m-%d").date()
        resultado = suggest_optimized_schedule(patient_id, exam_names, start_date)
        
        if resultado:
            return jsonify(resultado), 200
        else:
            return jsonify({"erro": "Não foi possível encontrar um horário para realizar todos os exames em sequência nos próximos 30 dias."}), 404
            
    except ValueError as ve: return jsonify({"erro": str(ve)}), 400
    except Exception as e: return jsonify({"erro": "Ocorreu um erro interno no servidor."}), 500

@bp.route('/buscar-todos-horarios', methods=['POST'])
def handle_busca_todos_horarios():
    data = request.get_json()
    exam_names = data.get('exam_names')
    target_date_str = data.get('data')

    if not all([exam_names, target_date_str]):
        return jsonify({"erro": "exam_names e data são obrigatórios."}), 400
        
    try:
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        horarios = get_all_available_slots_for_exams(exam_names, target_date)
        return jsonify({"horarios_disponiveis": horarios}), 200
    except ValueError as ve: return jsonify({"erro": str(ve)}), 400
    except Exception as e: return jsonify({"erro": "Ocorreu um erro interno no servidor."}), 500

@bp.route('/agendar-em-horario-especifico', methods=['POST'])
def handle_agendamento_especifico():
    data = request.get_json()
    patient_id = data.get('patient_id')
    exam_names = data.get('exam_names')
    desired_start_time = data.get('desired_start_time')

    if not all([patient_id, exam_names, desired_start_time]):
        return jsonify({"erro": "patient_id, exam_names e desired_start_time são obrigatórios."}), 400

    try:
        resultado = schedule_exams_at_specific_time(patient_id, exam_names, desired_start_time)
        if resultado:
            return jsonify({"mensagem": "Exames agendados com sucesso!", "agendamentos": resultado}), 201
        else:
            return jsonify({"erro": "O horário solicitado não está mais disponível."}), 409
    except ValueError as ve: return jsonify({"erro": str(ve)}), 400
    except Exception as e: return jsonify({"erro": "Ocorreu um erro interno no servidor."}), 500