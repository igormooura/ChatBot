
import json
from datetime import datetime
from config import gemini_model, gemini_ready
from ..utils.normalizacao import normalizar_texto_geral

def gerar_explicacao_detalhada_com_gemini(sintomas, sugestoes):
    """
    Gera uma explicação detalhada sobre por que cada especialista sugerido é relevante 
    para os sintomas apresentados.
    """
    if not gemini_ready or not sugestoes:
        return None

    lista_sugestoes_texto = ", ".join([f'"{esp}"' for esp, score in sugestoes])

    prompt = f"""
        Sua tarefa é atuar como um assistente de saúde virtual e criar uma recomendação pessoal para um paciente, explicando como cada especialista sugerido pode ajudar com os seus sintomas específicos.

        **REGRAS E FORMATO DE SAÍDA:**
        1.  **TOM PESSOAL E DIRETO:** Fale diretamente com o paciente. Use frases como "Dado que você sente..." ou "Um cardiologista pode investigar seus sintomas de...". O foco é o paciente, não a definição da especialidade.
        2.  **AVISO OBRIGATÓRIO:** Sempre comece sua resposta com o seguinte aviso em uma linha separada: "Aviso: As informações a seguir são sugestões educacionais e não substituem uma avaliação médica profissional. Procure um médico para obter um diagnóstico."
        3.  **FORMATO ESTRITO:** Para cada especialista, escreva o nome do especialista seguido de dois pontos, pule uma linha, e então escreva a explicação.
        4.  **SEM FORMATAÇÃO EXTRA:** Não use Markdown (negrito, etc.). Apenas texto puro.

        ---
        **EXEMPLO DE RESPOSTA ESPERADA (demonstrando o tom pessoal):**

        Aviso: As informações a seguir são sugestões educacionais e não substituem uma avaliação médica profissional. Procure um médico para obter um diagnóstico.

        Neurologista:
        Como você mencionou dor de cabeça forte e tontura, o neurologista é o especialista mais indicado. Ele poderá investigar a fundo a causa desses sintomas, descartar problemas mais sérios e encontrar um tratamento para aliviar sua dor.

        Clínico Geral:
        Uma consulta com o clínico geral é um ótimo primeiro passo. Baseado nos seus sintomas de dor de cabeça e tontura, ele pode fazer uma avaliação inicial para ver se a causa é algo mais simples, como estresse ou desidratação, e te direcionar corretamente se for preciso.
        ---

        **AGORA, APLIQUE AS REGRAS E O FORMATO AOS DADOS REAIS ABAIXO:**

        Sintomas do usuário: "{sintomas}"
        Especialistas sugeridos: {lista_sugestoes_texto}

        Sua resposta:
        """
    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"ERRO ao chamar a API do Gemini para explicação detalhada: {e}")
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

def formatar_horarios_com_gemini(info_pedido, horarios_encontrados):
    """
    Usa o Gemini para criar uma resposta em linguagem natural com a lista de horários.
    """
    if not gemini_ready:
        return "Desculpe, nosso assistente virtual está indisponível no momento."

    horarios_json = json.dumps(horarios_encontrados, indent=2, ensure_ascii=False)
 
    data_formatada = ""
    if info_pedido.get("data_base"):
        data_obj = datetime.strptime(info_pedido["data_base"], "%Y-%m-%d")
        data_formatada = data_obj.strftime("%d/%m/%Y")

    periodo = info_pedido.get("periodo_dia", "qualquer horário")
    especialista = info_pedido.get("especialista", "médico")

    prompt = f"""
    Sua tarefa é atuar como um assistente de agendamento, com um tom prestativo, claro e amigável.
    Você receberá uma solicitação de agendamento e uma lista de horários disponíveis em formato JSON.
    Sua resposta deve ser um texto em português do Brasil, apresentando os horários de forma organizada.

    **Regras Importantes:**
    1.  Se a lista de horários (JSON) estiver vazia (`[]`), informe ao usuário de forma educada que não foram encontrados horários para os critérios informados e sugira que ele tente outra data ou período.
    2.  Se houver horários, agrupe-os por nome do médico.
    3.  Formate os horários para serem fáceis de ler (ex: "09:30" em vez de "09:30:00").
    4.  Comece a resposta confirmando a busca do usuário (ex: "Ótima notícia! Encontrei alguns horários para cardiologista...").

    ---
    **Exemplo 1: Com Horários Encontrados**

    **Solicitação do Usuário:** Cardiologista para o dia 29/06/2025 na parte da tarde.
    **Lista de Horários (JSON):**
    [
      {{
        "medico_nome": "Dr. Carlos Andrade",
        "horario": "2025-06-29 14:00"
      }},
      {{
        "medico_nome": "Dra. Ana Silva",
        "horario": "2025-06-29 15:30"
      }},
      {{
        "medico_nome": "Dr. Carlos Andrade",
        "horario": "2025-06-29 14:30"
      }}
    ]

    **Sua Resposta Esperada:**
    Ótima notícia! Encontrei os seguintes horários para Cardiologista no dia 29/06/2025, na parte da tarde:

    **Dr. Carlos Andrade:**
    - 14:00
    - 14:30

    **Dra. Ana Silva:**
    - 15:30

    Para agendar, basta me dizer o médico e o horário escolhido!
    ---
    **Exemplo 2: Sem Horários Encontrados**

    **Solicitação do Usuário:** Pediatra para o dia 01/07/2025 na parte da noite.
    **Lista de Horários (JSON):**
    []

    **Sua Resposta Esperada:**
    Puxa, não encontrei nenhum horário disponível para Pediatra no dia 01/07/2025, na parte da noite. Que tal tentarmos em outra data ou período?
    ---

    **AGORA, APLIQUE AS REGRAS AOS DADOS REAIS ABAIXO:**

    **Solicitação do Usuário:** {especialista.capitalize()} para o dia {data_formatada} na parte da {periodo}.
    **Lista de Horários (JSON):**
    {horarios_json}

    **Sua Resposta:**
    """
    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"ERRO ao formatar horários com Gemini: {e}")
        return "Ocorreu um erro ao buscar os horários. Por favor, tente novamente."        