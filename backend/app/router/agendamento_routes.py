

from flask import Blueprint, request, jsonify
from datetime import datetime

from ..services.gemini_service import gerar_explicacao_com_gemini, analisar_pedido_com_gemini
from ..services.qdrant_service import sugerir_especialistas_qdrant
from ..models.agenda_model import filtrar_agenda_disponivel, registrar_consulta_model

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/sugerir-especialista', methods=['POST'])
def handle_sugestao():
    data = request.get_json()
    if not data or 'sintomas' not in data:
        return jsonify({"erro": "O campo 'sintomas' é obrigatório."}), 400

    sintomas = data['sintomas']
    sugestoes_qdrant = sugerir_especialistas_qdrant(sintomas)

    if not sugestoes_qdrant:
        return jsonify({"mensagem": "Não foi possível encontrar um especialista com base nos sintomas fornecidos."})

    explicacao_gemini = gerar_explicacao_com_gemini(sintomas, sugestoes_qdrant)
    
    horarios_disponiveis = []
    for esp_tupla in sugestoes_qdrant:
        nome_esp = esp_tupla[0] 
        info_pedido = {"especialista": nome_esp}
        horarios_filtrados = filtrar_agenda_disponivel(info_pedido)
        for horario in horarios_filtrados:
             horarios_disponiveis.append({
                "especialista": nome_esp.capitalize(),
                "horario": horario
            })
    horarios_disponiveis.sort(key=lambda x: x['horario'])

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
    
    horarios_filtrados = filtrar_agenda_disponivel(info_extraida)

    return jsonify({
        "pedido_entendido": info_extraida,
        "horarios_encontrados": horarios_filtrados
    })

@bp.route('/confirmar-agendamento', methods=['POST'])
def handle_confirmacao():
    data = request.get_json()
    nome = data.get('nome_paciente')
    especialista = data.get('especialista')
    horario = data.get('horario')

    if not all([nome, especialista, horario]):
        return jsonify({"erro": "Os campos 'nome_paciente', 'especialista' e 'horario' são obrigatórios."}), 400
    
    sucesso = registrar_consulta_model(nome, especialista, horario)

    if sucesso:
        dt_obj = datetime.strptime(horario, "%Y-%m-%d %H:%M")
        return jsonify({"mensagem": f"Consulta confirmada para {nome} com {especialista.capitalize()} em {dt_obj.strftime('%d/%m/%Y às %H:%M')}!"})
    else:
        return jsonify({"erro": "O horário selecionado não está mais disponível ou é inválido."}), 409