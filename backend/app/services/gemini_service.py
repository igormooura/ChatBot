import json
from datetime import datetime, timedelta
from config import gemini_model, gemini_ready
from ..utils.normalizacao import normalizar_texto_geral
from ..models.exames_model import EXAMES_DISPONIVEIS_CLINICA

ESPECIALIDADES_VALIDAS = [
    "Cardiologia",
    "Dermatologia",
    "Ortopedia",
    "Gastroenterologia",
    "Neurologia",
    "Oftalmologia",
    "Otorrinolaringologia",
    "Endocrinologia",
    "Pneumologia",
    "Urologia",
    "Ginecologia",
    "Clínica Geral"
]

def gerar_explicacao_com_gemini(sintomas, sugestoes):
    if not gemini_ready:
        return "Não foi possível conectar ao nosso assistente de IA no momento."

    lista_sugestoes_texto = "\n".join([f"- {esp}" for esp, score in sugestoes])

    prompt = f"""
    Sua tarefa é atuar como um assistente de saúde virtual empático e responsável.
    Baseado nos sintomas do usuário e na lista de especialistas sugeridos, gere uma explicação clara e útil.

    **Instruções Obrigatórias:**

    1.  **Aviso Inicial:** Comece a sua resposta, SEMPRE e EXATAMENTE, com a frase:
        "É importante lembrar que sou um assistente virtual e minhas sugestões não substituem a avaliação de um médico. Para um diagnóstico preciso, consulte um profissional de saúde."

    2.  **Explicação Detalhada:** Após o aviso, explique de forma didática o motivo da sugestão de CADA especialista, conectando-o diretamente aos sintomas informados.

    3.  **Formato do Título:** Antes da explicação de cada especialista, insira um título claro envolvido por ###.
        Exemplo de formato:
        ### Neurologista ###
        A explicação sobre o neurologista vem aqui...
        ### Clínico Geral ###
        A explicação sobre o clínico geral vem aqui...
    
    4.  **Tom e Estilo:** Mantenha um tom tranquilizador e uma linguagem simples. Não use jargões médicos complexos, não faça perguntas e não dê conselhos médicos diretos.

    **Dados para análise:**

    * **Sintomas informados pelo usuário:** "{sintomas}"
    * **Especialistas sugeridos para estes sintomas:**
        {lista_sugestoes_texto}

    **Inicie sua resposta agora, seguindo todas as instruções.**
    """
    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"ERRO ao chamar a API do Gemini para explicação: {e}")
        return "Tivemos um problema ao gerar a explicação. Por favor, tente novamente."

def analisar_pedido_com_gemini(texto_usuario):
    """
    MODIFICADO: Usa o Gemini para extrair uma LISTA de especialidades,
    além da data e período.
    """
    if not gemini_ready:
        return None

    data_hoje = datetime.now().strftime("%Y-%m-%d")
    
    prompt = f"""
    Sua tarefa é analisar o texto do usuário e extrair informações para um agendamento de consulta médica.
    A data de referência para hoje é: {data_hoje}.
    Responda APENAS com um objeto JSON válido.
    
    O JSON deve ter as seguintes chaves:
    - "especialistas": array de strings (os nomes das especialidades, normalizadas para os valores válidos)
    - "data_base": string (a data no formato "AAAA-MM-DD")
    - "periodo_dia": string ("manha", "tarde", ou "noite")

    **Instrução Crítica:** A chave "especialistas" DEVE conter um ou mais dos seguintes valores: {ESPECIALIDADES_VALIDAS}.
    Se o usuário pedir por "cardiologista e dermatologista", você deve retornar ["Cardiologia", "Dermatologia"].

    Se uma informação não for encontrada, o valor correspondente deve ser `null`.

    Exemplo 1:
    Texto: "quero marcar um cardiologista e um ortopedista para amanhã de tarde"
    JSON: {{"especialistas": ["Cardiologia", "Ortopedia"], "data_base": "{(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')}", "periodo_dia": "tarde"}}

    Agora, analise o seguinte texto:
    Texto: "{texto_usuario}"
    JSON: 
    """
    try:
        response = gemini_model.generate_content(prompt)
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_text)
    except Exception as e:
        print(f"ERRO ao analisar pedido com Gemini: {e}")
        return None

def identificar_exames_com_gemini(texto_pdf):
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


def analisar_data_exame_com_gemini(texto_usuario: str) -> dict | None:
    """
    Usa o Gemini para extrair APENAS a data e o período do texto do usuário para agendamento de exame.
    """
    if not gemini_model:
        print("Modelo Gemini não inicializado.")
        return {
            "data_base": (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            "periodo_dia": "qualquer"
        }

    data_hoje = datetime.now().strftime("%Y-%m-%d")
    
    prompt = f"""
    Sua tarefa é analisar o texto do usuário e extrair a data e o período do dia para um agendamento de exame.
    A data de referência para 'hoje' é: {data_hoje}.
    Responda APENAS com um objeto JSON válido.
    
    O JSON deve ter as seguintes chaves:
    - "data_base": string (a data no formato "AAAA-MM-DD")
    - "periodo_dia": string ("manha", "tarde", ou "qualquer")

    Se uma informação não for encontrada, o valor correspondente deve ser a data de amanhã para "data_base" e "qualquer" para "periodo_dia".

    Exemplo 1:
    Texto: "quero marcar para dia 29/07 no período da manhã"
    JSON: {{"data_base": "2025-07-29", "periodo_dia": "manha"}}

    Exemplo 2:
    Texto: "pode ser na próxima sexta"
    JSON: {{"data_base": "2025-08-01", "periodo_dia": "qualquer"}}

    Agora, analise o seguinte texto:
    Texto: "{texto_usuario}"
    JSON: 
    """
    try:
        response = gemini_model.generate_content(prompt)
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_text)
    except Exception as e:
        print(f"ERRO ao analisar data de exame com Gemini: {e}")
        return None
    