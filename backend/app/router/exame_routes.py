from flask import Blueprint, request, jsonify
from ..services.exame_service import find_and_schedule_sequential_exams

bp = Blueprint('exames', __name__, url_prefix='/exames')

@bp.route('/agendar-sequencial', methods=['POST'])
def handle_agendamento_exames():
    """
    Endpoint para agendar uma sequência de exames para um paciente.
    Espera um JSON com:
    {
        "patient_id": 10,
        "exam_names": ["Hemograma Completo", "Raio-X do Tórax"]
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Requisição JSON inválida."}), 400

    patient_id = data.get('patient_id')
    exam_names = data.get('exam_names')

    if not all([patient_id, exam_names and isinstance(exam_names, list)]):
        return jsonify({"erro": "patient_id e uma lista de exam_names são obrigatórios."}), 400

    try:
        horarios_agendados = find_and_schedule_sequential_exams(patient_id, exam_names)

        if horarios_agendados:
            agendamentos_formatados = [
                {"exame": name, "horario": dt.isoformat()}
                for name, dt in zip(exam_names, horarios_agendados)
            ]
            return jsonify({
                "mensagem": "Exames agendados com sucesso!",
                "agendamentos": agendamentos_formatados
            }), 201 # 201 Created é o status ideal para sucesso
        else:
            return jsonify({
                "erro": "Não foi possível encontrar um bloco de horário disponível para a sequência de exames solicitada."
            }), 409 # 409 Conflict indica que a requisição é válida mas não pode ser completada
            
    except ValueError as ve:
        # Erro caso um nome de exame não seja encontrado no DB
        return jsonify({"erro": str(ve)}), 404
    except Exception as e:
        # Erro genérico para problemas inesperados (ex: falha no DB)
        print(f"ERRO INESPERADO NA ROTA: {e}")
        return jsonify({"erro": "Ocorreu um erro interno no servidor."}), 500