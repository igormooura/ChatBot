from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

from ..services.exame_service import (
    find_and_schedule_optimized_exams, 
    schedule_exams_at_specific_time
)

bp = Blueprint('exames', __name__, url_prefix='/exames')

@bp.route('/sugerir-e-agendar', methods=['POST'])
def handle_sugestao_exames():
    """
    Exemplo: {"patient_id": 10, "exam_names": ["Exame A", "Exame B"]}
    """
    data = request.get_json()
    if not data: return jsonify({"erro": "Requisição JSON inválida."}), 400

    patient_id = data.get('patient_id')
    exam_names = data.get('exam_names')

    if not all([patient_id, exam_names and isinstance(exam_names, list)]):
        return jsonify({"erro": "patient_id e uma lista de exam_names são obrigatórios."}), 400

    try:
        resultado = find_and_schedule_optimized_exams(patient_id, exam_names)
        if resultado:

            agendamentos_detalhados = []
            start_time = datetime.fromisoformat(resultado['start_time'])
            current_time = start_time
            EXAM_DURATION = timedelta(minutes=30) 

            for exam_name in resultado['scheduled_order']:
                agendamentos_detalhados.append({
                    "exame": exam_name,
                    "horario": current_time.isoformat()
                })
                current_time += EXAM_DURATION

            return jsonify({
                "mensagem": "Exames agendados com sucesso na primeira oportunidade encontrada!",
                "agendamentos": agendamentos_detalhados
            }), 201
        else:
            return jsonify({
                "erro": "Não foi possível encontrar um bloco de horário disponível, mesmo otimizando a ordem."
            }), 409
            
    except ValueError as ve:
        return jsonify({"erro": str(ve)}), 404
    except Exception as e:
        print(f"ERRO INESPERADO NA ROTA: {e}")
        return jsonify({"erro": "Ocorreu um erro interno no servidor."}), 500

@bp.route('/agendar-em-horario-especifico', methods=['POST'])
def handle_agendamento_especifico():
    """
    Exemplo: {
        "patient_id": 10,
        "exam_names": ["Exame A", "Exame B"],
        "desired_start_time": "2025-07-16T14:00:00"
    }
    """
    data = request.get_json()
    if not data: return jsonify({"erro": "Requisição JSON inválida."}), 400

    patient_id = data.get('patient_id')
    exam_names = data.get('exam_names')
    desired_start_time = data.get('desired_start_time')

    if not all([patient_id, exam_names, desired_start_time]):
        return jsonify({"erro": "patient_id, exam_names e desired_start_time são obrigatórios."}), 400

    try:
        resultado = schedule_exams_at_specific_time(patient_id, exam_names, desired_start_time)
        if resultado:
            agendamentos_detalhados = []
            start_time = datetime.fromisoformat(resultado['start_time'])
            current_time = start_time
            EXAM_DURATION = timedelta(minutes=30)

            for exam_name in resultado['scheduled_order']:
                agendamentos_detalhados.append({
                    "exame": exam_name,
                    "horario": current_time.isoformat()
                })
                current_time += EXAM_DURATION

            return jsonify({
                "mensagem": "Exames agendados com sucesso no horário solicitado!",
                "agendamentos": agendamentos_detalhados
            }), 201
        else:
            return jsonify({
                "erro": "O horário solicitado não está disponível, mesmo tentando otimizar a ordem dos exames."
            }), 409

    except ValueError as ve:
        return jsonify({"erro": str(ve)}), 400
    except Exception as e:
        print(f"ERRO INESPERADO NA ROTA: {e}")
        return jsonify({"erro": "Ocorreu um erro interno no servidor."}), 500
