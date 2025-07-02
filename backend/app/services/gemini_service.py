# backend/services/gemini_service.py

import json
from datetime import datetime
from config import gemini_model, gemini_ready
from ..utils.normalizacao import normalizar_texto_geral

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