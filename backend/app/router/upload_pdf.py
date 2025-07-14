from flask import render_template, request, Blueprint, jsonify, current_app
from werkzeug.utils import secure_filename
import os

from ..services.arquivo_service import extrair_texto_pdf
from ..services.gemini_service import identificar_exames_com_gemini
bp = Blueprint('api_upload', __name__, url_prefix='/api/upload')

@bp.route('/pdf', methods=['GET', 'POST'])
def upload_arquivo():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"erro": "O campo 'file' é obrigatório."}), 400

        file = request.files.get('file')
        if not file or file.filename == '':
            return jsonify({"erro": "Nenhum arquivo selecionado."}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        resultado_extracao = extrair_texto_pdf(filepath)
        os.remove(filepath)
        
        if not resultado_extracao.get("success"):
            return jsonify({"erro": resultado_extracao.get("error")}), 500

        texto_do_pdf = resultado_extracao.get("text")

        resultado_llm = identificar_exames_com_gemini(texto_do_pdf)

        if "erro" in resultado_llm:
            return jsonify(resultado_llm), 500

        return jsonify({
            "mensagem": "Guia de exame analisada com sucesso.",
            "exames_encontrados": resultado_llm.get("exames_encontrados", []),
            "texto_extraido_do_pdf": texto_do_pdf
        })
        
    return render_template('upload.html', message='')