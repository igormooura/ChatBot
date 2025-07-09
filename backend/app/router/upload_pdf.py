from flask import render_template, request, Blueprint, jsonify, current_app
from werkzeug.utils import secure_filename
import os

from ..services.arquivo_service import extrair_texto_pdf, identificar_tipo_exame

bp = Blueprint('api_upload', __name__, url_prefix='/api/upload')

@bp.route('/pdf', methods=['GET', 'POST'])
def upload_arquivo():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"erro": "O campo 'file' é obrigatório."}), 400

        file = request.files['file']
        if file.filename == '':
            return render_template('upload.html', message="Nenhum arquivo selecionado")
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            resultado_extração = extrair_texto_pdf(filepath)
            os.remove(filepath)

            if resultado_extração["success"]:
                texto_do_pdf = resultado_extração["text"]
                tipo_exame = identificar_tipo_exame(texto_do_pdf)

                return jsonify({
                    "message": "Arquivo lido com sucesso",
                    "tipo_exame": tipo_exame
                })
            #return render_template('upload.html', message="Arquivo gravado")
        
        
    return render_template('upload.html', message='')