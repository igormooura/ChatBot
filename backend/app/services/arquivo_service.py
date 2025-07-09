import os
import PyPDF2

def extrair_texto_pdf(caminho_arquivo):
    """
    Extrai texto de um arquivo PDF usando PyPDF2.
    """
    try:
        with open(caminho_arquivo, 'rb') as arquivo_pdf:
            leitor_pdf = PyPDF2.PdfReader(arquivo_pdf)
            texto_extraido = ""
            for pagina in leitor_pdf.pages:
                texto_extraido += pagina.extract_text() + "\n"
        return {"success": True, "text": texto_extraido}
    except PyPDF2.errors.PdfReadError:
        return {"success": False, "error": "O arquivo PDF parece estar corrompido ou protegido por senha."}
    except FileNotFoundError:
        return {"success": False, "error": "Erro interno: O arquivo PDF temporário não foi encontrado."}
    except Exception as e:
        return {"success": False, "error": f"Ocorreu um erro inesperado ao ler o PDF: {e}"}

def identificar_tipo_exame(texto_pdf):
    """
    Tenta identificar o tipo de exame no texto extraído.
    """
    tipos_comuns = {
        "hemograma": "Hemograma Completo",
        "ultrassonografia": "Ultrassonografia",
        "ressonancia": "Ressonância Magnética",
        "raio-x": "Raio-X",
        "glicemia": "Exame de Glicemia",
        "colesterol": "Exame de Colesterol"
    }
    texto_minusculo = texto_pdf.lower()
    for palavra_chave, tipo in tipos_comuns.items():
        if palavra_chave in texto_minusculo:
            return tipo
    return "Tipo de exame não identificado"