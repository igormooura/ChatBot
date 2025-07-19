from flask import Blueprint, request, jsonify
from datetime import datetime

from ..services.gemini_service import gerar_explicacao_com_gemini, analisar_pedido_com_gemini
from ..services.qdrant_service import sugerir_especialistas_qdrant
from ..services.agendamento_service import buscar_horarios_disponiveis_db, confirmar_agendamento_db

bp = Blueprint('api', __name__, url_prefix='/api/agendamento')

@bp.route('/sugerir-especialista', methods=['POST'])
def handle_sugestao():
    data = request.get_json()
    if not data or 'sintomas' not in data:
        return jsonify({"erro": "O campo 'sintomas' é obrigatório."}), 400

    sintomas = data['sintomas']
    sugestoes_qdrant = sugerir_especialistas_qdrant(sintomas)

    if not sugestoes_qdrant:
        return jsonify({"mensagem": "Não foi possível encontrar um especialista com base nos sintomas fornecidos."}), 400

    primeiro_especialista = sugestoes_qdrant[0][0] if sugestoes_qdrant else None
    
    horarios_disponiveis = []
    if primeiro_especialista:
        info_pedido = {"especialista": primeiro_especialista}
        horarios_disponiveis = buscar_horarios_disponiveis_db(info_pedido)

    explicacao_gemini = gerar_explicacao_com_gemini(sintomas, sugestoes_qdrant)

    return jsonify({
        "explicacao": explicacao_gemini,
        "horarios_sugeridos": horarios_disponiveis[:5] 
    })


@bp.route('/buscar-horarios', methods=['POST'])
def handle_busca_direta():
    data = request.get_json()
    if not data or 'pedido' not in data:
        return jsonify({"erro": "O campo 'pedido' é obrigatório."}), 400

    pedido = data['pedido']
    info_extraida = analisar_pedido_com_gemini(pedido)

    if not info_extraida or not info_extraida.get('especialista'):
        return jsonify({"erro": "Não foi possível entender o seu pedido. Tente ser mais específico."}), 400
    
    horarios_filtrados = buscar_horarios_disponiveis_db(info_extraida)

    return jsonify({
        "pedido_entendido": info_extraida,
        "horarios_encontrados": horarios_filtrados
    })


@bp.route('/confirmar-agendamento', methods=['POST'])
def handle_confirmacao():
    data = request.get_json()
    nome_paciente = data.get('nome_paciente')
    medico_id = data.get('medico_id') 
    horario = data.get('horario')

    if not all([nome_paciente, medico_id, horario]):
        return jsonify({"erro": "Os campos 'nome_paciente', 'medico_id' e 'horario' são obrigatórios."}), 400
    
    agendamento_confirmado = confirmar_agendamento_db(nome_paciente, medico_id, horario)

    if agendamento_confirmado:
        nome_medico = agendamento_confirmado.doctor.name
        especialidade_medico = agendamento_confirmado.doctor.specialty
        dt_obj = agendamento_confirmado.date
        
        mensagem = (f"Consulta confirmada para {nome_paciente} com Dr(a). {nome_medico} "
                    f"({especialidade_medico.capitalize()}) em {dt_obj.strftime('%d/%m/%Y às %H:%M')}!")
        
        return jsonify({"mensagem": mensagem})
    else:
        return jsonify({"erro": "O horário selecionado não está mais disponível ou é inválido."}), 409