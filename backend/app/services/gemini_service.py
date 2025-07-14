import json
from datetime import datetime
from config import gemini_model, gemini_ready
from ..utils.normalizacao import normalizar_texto_geral
import json
from ..models.exames_model import EXAMES_DISPONIVEIS_CLINICA

def gerar_explicacao_com_gemini(sintomas, sugestoes):
    if not gemini_ready:
        return None

    lista_sugestoes_texto = "\n".join([f"- {esp}" for esp, score in sugestoes])
    prompt = f"""
    Você é um assistente de saúde virtual. Analise os sintomas e as sugestões de especialistas e gere uma explicação curta (2-3 frases) em português do Brasil, explicando por que essas sugestões fazem sentido. NÃO dê conselhos médicos e NÃO faça perguntas.

    Sintomas: "{sintomas}"
    Sugestões:
    {lista_sugestoes_texto}

    Explicação:
    """
    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"ERRO ao chamar a API do Gemini para explicação: {e}")
        return None

def analisar_pedido_com_gemini(texto_usuario):
    if not gemini_ready:
        return None

    data_hoje = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""
    Sua tarefa é analisar o texto do usuário e extrair informações para um agendamento de consulta médica.
    A data de referência para hoje é: {data_hoje}.
    Responda APENAS com um objeto JSON válido.
    
    O JSON deve ter as seguintes chaves:
    - "especialista": string (o nome da especialidade médica, normalizada e em minúsculas, ex: "cardiologista")
    - "data_base": string (a data no formato "AAAA-MM-DD")
    - "periodo_dia": string ("manha", "tarde", ou "noite")

    Se uma informação não for encontrada, o valor correspondente deve ser `null`.

    Exemplo:
    Texto: "quero marcar um cardiologista para amanhã de tarde"
    JSON: {{"especialista": "cardiologista", "data_base": "2025-06-29", "periodo_dia": "tarde"}}

    Agora, analise o seguinte texto:
    Texto: "{texto_usuario}"
    JSON: 
    """
    try:
        response = gemini_model.generate_content(prompt)
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        info_extraida = json.loads(json_text)

        if info_extraida.get("especialista"):
            info_extraida["especialista"] = normalizar_texto_geral(info_extraida["especialista"])
        
        return info_extraida
    except Exception as e:
        print(f"ERRO ao analisar pedido com Gemini: {e}")
        return None
    
def identificar_exames_com_gemini(texto_pdf):
    """
    Usa a LLM para analisar o texto de uma guia de exame e identificar
    quais exames da lista da clínica estão sendo solicitados.
    
    Args:
        texto_pdf (str): O texto completo extraído da guia de exame em PDF.

    Returns:
        dict: Um dicionário contendo a lista de exames encontrados ou um erro.
    """
    if not gemini_ready:
        print("ERRO: Serviço do Gemini não está pronto.")
        return {"erro": "Serviço de IA indisponível."}

    lista_formatada = "\n".join([f"- {exame}" for exame in EXAMES_DISPONIVEIS_CLINICA])

    prompt = f"""
    Você é um assistente administrativo de uma clínica. Sua tarefa é analisar o texto de uma guia de exames enviada por um paciente e identificar quais exames solicitados correspondem à lista de exames que a clínica oferece.

    **Instruções:**
    1. Leia o "Texto da Guia de Exame" abaixo.
    2. Compare os exames mencionados no texto com a "Lista de Exames da Clínica".
    3. Retorne APENAS um objeto JSON contendo uma única chave chamada "exames_encontrados", que deve ser uma lista de strings.
    4. A lista de strings deve conter APENAS os nomes dos exames da "Lista de Exames da Clínica" que foram encontrados no texto.
    5. Se nenhum exame correspondente for encontrado, retorne uma lista vazia. Não inclua exames que não estão na lista da clínica.

    **Lista de Exames da Clínica:**
    {lista_formatada}

    **Texto da Guia de Exame:**
    ---
    {texto_pdf}
    ---

    **JSON de Resposta:**
    """

    try:
        response = gemini_model.generate_content(prompt)
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        resultado = json.loads(json_text)

        if isinstance(resultado, dict) and "exames_encontrados" in resultado and isinstance(resultado["exames_encontrados"], list):
             return resultado
        else:
            print("ERRO: A resposta da LLM não está no formato JSON esperado.")
            return {"erro": "Não foi possível processar a resposta da IA."}

    except Exception as e:
        print(f"ERRO ao chamar a API do Gemini para identificar exames: {e}")
        return {"erro": f"Ocorreu um erro na comunicação com a IA: {e}"}