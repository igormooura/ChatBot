
from flask import Blueprint, request, jsonify
from datetime import datetime
from ..services.gemini_service import analisar_pedido_com_gemini, gerar_explicacao_com_gemini
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
        return jsonify({"mensagem": "Não foi possível encontrar um especialista."}), 400
    primeiro_especialista = sugestoes_qdrant[0][0] if sugestoes_qdrant else None
    horarios_disponiveis = []
    if primeiro_especialista:
        info_pedido = {"especialista": primeiro_especialista} # A função de busca aqui espera um só
        horarios_disponiveis = buscar_horarios_disponiveis_db(info_pedido)
    explicacao_gemini = gerar_explicacao_com_gemini(sintomas, sugestoes_qdrant)
    return jsonify({
        "explicacao": explicacao_gemini,
        "horarios_sugeridos": horarios_disponiveis[:5] 
    })


@bp.route('/buscar-horarios', methods=['POST'])
def handle_busca_direta():
    """
    MODIFICADO: Agora esta rota lida corretamente com a lista de especialistas
    retornada pelo Gemini.
    """
    data = request.get_json()
    if not data or 'pedido' not in data:
        return jsonify({"erro": "O campo 'pedido' é obrigatório."}), 400
    
    pedido = data['pedido']
    info_extraida = analisar_pedido_com_gemini(pedido)

    if not info_extraida or not info_extraida.get('especialistas') or not isinstance(info_extraida.get('especialistas'), list):
        return jsonify({"erro": "Não foi possível entender o seu pedido. Tente ser mais específico com as especialidades."}), 400

    horarios_filtrados = buscar_horarios_disponiveis_db(info_extraida)

    if not horarios_filtrados:
        return jsonify({
            "pedido_entendido": info_extraida,
            "horarios_encontrados": [],
            "mensagem": "Nenhum horário encontrado para os critérios selecionados."
        }), 404

    return jsonify({
        "pedido_entendido": info_extraida,
        "horarios_encontrados": horarios_filtrados
    })


@bp.route('/confirmar-agendamento', methods=['POST'])
def handle_confirmacao():
    data = request.get_json()
    email = data.get('email')
    cpf = data.get('cpf')
    agendamentos = data.get('agendamentos') 

    if not all([email, cpf, agendamentos]):
        return jsonify({"erro": "Os campos 'email', 'cpf' e 'agendamentos' (lista) são obrigatórios."}), 400
    
    agendamentos_confirmados, erros = confirmar_agendamento_db(email, cpf, agendamentos)

    if erros:
        return jsonify({"erro": "Alguns horários não puderam ser confirmados.", "detalhes": erros}), 409
    
    if agendamentos_confirmados:
        total = len(agendamentos_confirmados)
        plural_s = "s" if total > 1 else ""
        mensagem = f"{total} consulta{plural_s} confirmada{plural_s} com sucesso!"
        return jsonify({"mensagem": mensagem})
    else:
        return jsonify({"erro": "Não foi possível processar o seu pedido de agendamento."}), 500