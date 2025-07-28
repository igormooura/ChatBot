from flask import Blueprint, request, jsonify
from datetime import datetime
from ..services.exame_service import (
    suggest_optimized_schedule,
    get_all_available_slots_for_exams,
    schedule_exams_at_specific_time,
    suggest_alternative_days,
    schedule_manual_exams
)
from ..services.gemini_service import analisar_data_exame_com_gemini

bp = Blueprint('exames', __name__, url_prefix='/api/exames')

@bp.route('/sugerir-horario-otimizado', methods=['POST'])
def handle_sugestao_otimizada():
    data = request.get_json()
    patient_id = data.get('patient_id', 1) 
    exam_names = data.get('exam_names')
    pedido_data_texto = data.get('pedido_data')

    if not all([exam_names, pedido_data_texto]):
        return jsonify({"erro": "exam_names e pedido_data são obrigatórios."}), 400
    
    try:
        analise = analisar_data_exame_com_gemini(pedido_data_texto)
        if not analise or not analise.get('data_base'):
            return jsonify({"erro": "Não foi possível entender a data informada."}), 400
        
        data_inicio_str = analise['data_base']
        periodo_dia = analise.get('periodo_dia', 'qualquer')
        data_inicio_dt = datetime.strptime(data_inicio_str, "%Y-%m-%d").date()

        resultado = suggest_optimized_schedule(patient_id, exam_names, data_inicio_dt, periodo_dia)
        
        if resultado:
            return jsonify(resultado), 200
        else:
            return jsonify({"erro": f"Não foi possível encontrar uma sequência de horários a partir de {data_inicio_str} no período solicitado."}), 404
            
    except Exception as e:
        return jsonify({"erro": "Ocorreu um erro interno no servidor.", "details": str(e)}), 500

@bp.route('/sugerir-dias', methods=['POST'])
def handle_sugestao_dias():
    data = request.get_json()
    patient_id = data.get('patient_id', 1)
    exam_names = data.get('exam_names')
    pedido_data_texto = data.get('pedido_data')

    try:
        analise = analisar_data_exame_com_gemini(pedido_data_texto)
        data_inicio_dt = datetime.strptime(analise['data_base'], "%Y-%m-%d").date()
        periodo_dia = analise.get('periodo_dia', 'qualquer')

        sugestoes = suggest_alternative_days(patient_id, exam_names, data_inicio_dt, periodo_dia)
        if sugestoes:
            return jsonify({"dias_sugeridos": sugestoes}), 200
        else:
            return jsonify({"erro": "Não foram encontrados dias alternativos com horários sequenciais."}), 404
    except Exception as e:
        return jsonify({"erro": "Ocorreu um erro ao sugerir dias alternativos."}), 500

@bp.route('/agendar-manual', methods=['POST'])
def handle_agendamento_manual():
    data = request.get_json()
    email = data.get('email')
    cpf = data.get('cpf')
    selecoes = data.get('selecoes')

    if not all([email, cpf, selecoes]):
        return jsonify({"erro": "email, cpf e selecoes são obrigatórios."}), 400
    
    try:
        resultado = schedule_manual_exams(email, cpf, selecoes)
        return jsonify({"mensagem": "Exames agendados com sucesso!", "agendamentos": resultado}), 201
    except ValueError as ve:
        return jsonify({"erro": str(ve)}), 409
    except Exception as e:
        return jsonify({"erro": "Ocorreu um erro interno no servidor."}), 500

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
    except Exception as e:
        return jsonify({"erro": "Ocorreu um erro interno no servidor."}), 500

@bp.route('/agendar-em-horario-especifico', methods=['POST'])
def handle_agendamento_especifico():
    data = request.get_json()
    email = data.get('email')
    cpf = data.get('cpf')
    exam_names = data.get('exam_names')
    desired_start_time = data.get('desired_start_time')

    if not all([email, cpf, exam_names, desired_start_time]):
        return jsonify({"erro": "email, cpf, exam_names e desired_start_time são obrigatórios."}), 400
    
    try:
        resultado = schedule_exams_at_specific_time(
            email=email, cpf=cpf, exam_names=exam_names, desired_start_str=desired_start_time
        )
        if resultado:
            return jsonify({"mensagem": "Exames agendados com sucesso!", "agendamentos": resultado}), 201
        else:
            return jsonify({"erro": "O horário solicitado não está mais disponível ou é inválido."}), 409
    except ValueError as ve:
        return jsonify({"erro": str(ve)}), 400
    except Exception as e:
        return jsonify({"erro": "Ocorreu um erro interno no servidor."}), 500


@bp.route('/buscar-horarios-por-texto', methods=['POST'])
def handle_busca_horarios_por_texto():
    """
    Recebe um pedido em texto, extrai a data usando a função 
    analisar_data_exame_com_gemini e busca os horários disponíveis..
    """
    data = request.get_json()
    exam_names = data.get('exam_names')
    pedido_texto = data.get('pedido_texto')

    if not all([exam_names, pedido_texto]):
        return jsonify({"erro": "Os parâmetros exam_names e pedido_texto são obrigatórios."}), 400

    try:
        data_analisada = analisar_data_exame_com_gemini(pedido_texto)
        
        if not data_analisada or not data_analisada.get('data_base'):
            return jsonify({"erro": "Não foi possível identificar uma data no seu pedido. Tente ser mais específico."}), 400

        target_date_str = data_analisada.get('data_base')
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()

        horarios = get_all_available_slots_for_exams(exam_names, target_date)
        
        return jsonify({
            "data_entendida": target_date_str,
            "horarios_disponiveis": horarios
        }), 200
        
    except Exception as e:
        print(f"Erro em /buscar-horarios-por-texto: {e}")
        return jsonify({"erro": "Ocorreu um erro interno ao processar seu pedido."}), 500
    
