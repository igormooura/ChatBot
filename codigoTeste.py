import spacy
import re
import dateparser
from datetime import datetime
from collections import Counter

# --- CONFIGURAÇÃO INICIAL ---

# Carrega o modelo de linguagem do spaCy (usando o maior para melhor performance)
try:
    nlp = spacy.load("pt_core_news_lg")
except OSError:
    print("Modelo 'pt_core_news_lg' não encontrado. "
          "Por favor, instale-o executando: python -m spacy download pt_core_news_lg")
    exit()

# Definição de especialidades e palavras-chave para SUGESTÃO (versão mais completa)
ESPECIALISTAS_SINTOMAS = {
    "Cardiologista": ["coração", "peito", "dor no peito", "palpitação", "pressão alta", "falta de ar", "infarto", "angina", "taquicardia", "arritmia"],
    "Dermatologista": ["pele", "mancha", "coceira", "acne", "espinha", "cabelo", "queda de cabelo", "unha", "alergia de pele", "micose", "verruga", "psoríase", "dermatite"],
    "Ortopedista": ["osso", "articulação", "joelho", "coluna", "costas", "dor nas costas", "fratura", "torção", "dor muscular", "tendinite", "ombro", "quadril", "ligamento"],
    "Gastroenterologista": ["estômago", "azia", "refluxo", "náusea", "vômito", "diarreia", "intestino", "prisão de ventre", "gastrite", "úlcera", "digestão"],
    "Neurologista": ["cabeça", "dor de cabeça", "tontura", "vertigem", "convulsão", "memória", "formigamento", "dormência", "enxaqueca", "avc", "parkinson", "alzheimer"],
    "Oftalmologista": ["olho", "visão", "vista", "cegueira", "miopia", "astigmatismo", "hipermetropia", "óculos", "lente de contato", "catarata", "glaucoma", "conjuntivite"],
    "Otorrinolaringologista": ["ouvido", "dor de ouvido", "nariz", "garganta", "dor de garganta", "sinusite", "rinite", "tontura", "zumbido", "surdez", "rouquidão", "amigdalite"],
    "Endocrinologista": ["diabetes", "tireoide", "hormônio", "obesidade", "metabolismo", "crescimento", "colesterol"],
    "Pneumologista": ["pulmão", "respiração", "tosse", "chiado no peito", "asma", "bronquite", "pneumonia"],
    "Urologista": ["rim", "bexiga", "urina", "próstata", "infecção urinária", "cálculo renal"],
    "Ginecologista": ["útero", "ovário", "menstruação", "corrimento", "gravidez", "contracepção", "preventivo"],
    "Clínico Geral": ["geral", "febre", "cansaço", "mal-estar", "gripe", "resfriado", "check-up", "dor no corpo", "exames de rotina"]
}

# Simulação de banco de dados de AGENDA e consultas
agenda = {
    "cardiologista": {
        "2025-07-15 15:00": "disponível", # Ajustando para datas futuras
        "2025-07-15 16:00": "ocupado",
        "2025-07-16 10:00": "disponível",
    },
    "dermatologista": {
        "2025-07-17 09:00": "disponível",
        "2025-07-17 10:00": "disponível",
    },
    "ortopedista": {
        "2025-07-18 11:00": "disponível",
    },
    "clínico geral": { # Chave em minúsculo para consistência
        "2025-07-15 08:00": "disponível",
        "2025-07-15 09:00": "ocupado",
    }
}
consultas_registradas = []

# --- FUNÇÕES AUXILIARES ---

def normalizar_texto_sugestao(texto):
    """Normalização mais agressiva para a sugestão de especialista."""
    texto = texto.lower()
    texto = re.sub(r'[áàâãä]', 'a', texto)
    texto = re.sub(r'[éèêë]', 'e', texto)
    texto = re.sub(r'[íìîï]', 'i', texto)
    texto = re.sub(r'[óòôõö]', 'o', texto)
    texto = re.sub(r'[úùûü]', 'u', texto)
    texto = re.sub(r'[ç]', 'c', texto)
    texto = re.sub(r'[^a-z0-9\s]', '', texto) # Remove pontuação e outros caracteres
    return texto.strip()

def normalizar_texto_geral(texto):
    """Normalização mais leve para dateparser e extração geral."""
    texto = texto.lower()
    texto = re.sub(r'[áàâãä]', 'a', texto)
    texto = re.sub(r'[éèêë]', 'e', texto)
    texto = re.sub(r'[íìîï]', 'i', texto)
    texto = re.sub(r'[óòôõö]', 'o', texto)
    texto = re.sub(r'[úùûü]', 'u', texto)
    texto = re.sub(r'[ç]', 'c', texto)
    return texto.strip()

def sugerir_especialistas(descricao_sintomas):
    """
    Analisa a descrição dos sintomas e sugere especialistas.
    Retorna uma lista de tuplas (especialista, pontuação) ordenada pela pontuação.
    """
    if not descricao_sintomas:
        return []

    texto_normalizado_para_sugestao = normalizar_texto_sugestao(descricao_sintomas)
    # nlp(descricao_sintomas) # O processamento com spaCy pode ser usado para extrair lemmas se desejado,
                              # mas a lógica atual foca em correspondência de substrings.

    contagem_especialistas = Counter()

    for especialista, palavras_chave in ESPECIALISTAS_SINTOMAS.items():
        palavras_chave_normalizadas = [normalizar_texto_sugestao(chave) for chave in palavras_chave]
        score = 0
        for chave_norm in palavras_chave_normalizadas:
            if chave_norm in texto_normalizado_para_sugestao:
                score += texto_normalizado_para_sugestao.count(chave_norm)
                score += len(chave_norm.split()) -1 # Adiciona mais peso para palavras-chave mais longas
        
        if score > 0:
            contagem_especialistas[especialista] = score
            
    sugestoes_ordenadas = contagem_especialistas.most_common()
    return sugestoes_ordenadas

def extrair_info_agendamento(texto):
    """Extrai especialista e data/hora de um pedido de agendamento."""
    texto_norm_geral = normalizar_texto_geral(texto)
    especialidade_encontrada = None
    data_hora = None

    for esp_nome_mapa in agenda.keys(): # Nomes de especialista na agenda estão em minúsculo
        if esp_nome_mapa in texto_norm_geral:
            especialidade_encontrada = esp_nome_mapa
            texto_para_data = texto_norm_geral.replace(esp_nome_mapa, "").strip()
            data_hora = dateparser.parse(texto_para_data, languages=['pt'], settings={'PREFER_DATES_FROM': 'future', 'DATE_ORDER': 'DMY'})
            break
            
    return especialidade_encontrada, data_hora

def mostrar_horarios_disponiveis_com_opcoes(especialidade_nome_mapa):
    """Mostra os horários livres numerados e retorna a lista de horários (formato YYYY-MM-DD HH:MM)."""
    print(f"🤖 Estes são os horários disponíveis para {especialidade_nome_mapa.capitalize()}:")
    
    horarios_raw_disponiveis = [
        hora_str for hora_str, status in agenda.get(especialidade_nome_mapa, {}).items()
        if status == 'disponível'
    ]
    # Ordenar para consistência na apresentação
    horarios_raw_disponiveis.sort() 

    if horarios_raw_disponiveis:
        for i, horario_str in enumerate(horarios_raw_disponiveis):
            dt_obj = datetime.strptime(horario_str, "%Y-%m-%d %H:%M")
            print(f"   {i+1}. {dt_obj.strftime('%d/%m/%Y às %H:%M')}")
    else:
        print("   - Desculpe, não há horários disponíveis no momento para este especialista.")
    
    return horarios_raw_disponiveis # Retorna a lista de strings "YYYY-MM-DD HH:MM"

def verificar_agenda(especialidade_nome_mapa, data_hora_obj):
    """Verifica se um horário específico está disponível."""
    if especialidade_nome_mapa and data_hora_obj:
        data_formatada_str = data_hora_obj.strftime("%Y-%m-%d %H:%M")
        return agenda.get(especialidade_nome_mapa, {}).get(data_formatada_str, "não disponível")
    return "não disponível"

def registrar_consulta(nome_paciente, especialidade_nome_mapa, data_hora_obj):
    """Registra uma nova consulta e marca o horário como ocupado."""
    data_formatada_str = data_hora_obj.strftime("%Y-%m-%d %H:%M")
    agenda[especialidade_nome_mapa][data_formatada_str] = "ocupado" # Marcar como ocupado
    consultas_registradas.append({
        "nome": nome_paciente,
        "especialidade": especialidade_nome_mapa.capitalize(),
        "data_hora": data_formatada_str
    })
    print(f"✅ Consulta confirmada com sucesso para {nome_paciente} com {especialidade_nome_mapa.capitalize()} em {data_hora_obj.strftime('%d/%m/%Y às %H:%M')}!")

# --- CHATBOT PRINCIPAL (Lógica Híbrida Aprimorada) ---

def chatbot_hibrido():
    print("🤖 Olá! Sou seu assistente de saúde.")
    print("   Você pode descrever seus sintomas para eu sugerir um especialista,")
    print("   ou pode pedir diretamente para marcar uma consulta (ex: 'marcar dermatologista amanhã às 10h').")
    print("   Digite 'sair' a qualquer momento para encerrar.")
    print("-" * 50)

    # Contexto da conversa
    contexto_sugestoes_pendentes = None # Guarda a lista de [(especialista, score), ...]
    contexto_especialista_para_agendar = None # Guarda o nome do especialista (chave do dict 'agenda')
    contexto_horarios_oferecidos = None # Guarda a lista de strings de horários "YYYY-MM-DD HH:MM"

    while True:
        entrada_usuario = input("Você: ").strip()
        if entrada_usuario.lower() in ["sair", "encerrar", "tchau", "exit"]:
            print("🤖 Até logo! Cuide-se.")
            break

        # Resetar contextos de ação se o usuário não respondeu diretamente a eles
        input_lower = entrada_usuario.lower()
        is_numeric_choice = entrada_usuario.isdigit()

        # --- FLUXO 1: Usuário está escolhendo um HORÁRIO de uma lista numerada ---
        if contexto_especialista_para_agendar and contexto_horarios_oferecidos and is_numeric_choice:
            try:
                escolha_idx = int(entrada_usuario) - 1
                if 0 <= escolha_idx < len(contexto_horarios_oferecidos):
                    horario_escolhido_str = contexto_horarios_oferecidos[escolha_idx]
                    data_hora_obj_escolhida = datetime.strptime(horario_escolhido_str, "%Y-%m-%d %H:%M")
                    
                    nome_paciente = input(f"🤖 Ótima escolha! Para confirmar {contexto_especialista_para_agendar.capitalize()} em {data_hora_obj_escolhida.strftime('%d/%m/%Y às %H:%M')}, qual seu nome completo? ")
                    if nome_paciente:
                        registrar_consulta(nome_paciente, contexto_especialista_para_agendar, data_hora_obj_escolhida)
                    else:
                        print("🤖 Nome não fornecido. Agendamento cancelado.")
                    # Limpar contexto de agendamento
                    contexto_especialista_para_agendar = None
                    contexto_horarios_oferecidos = None
                    contexto_sugestoes_pendentes = None
                else:
                    print("🤖 Opção inválida. Por favor, escolha um número da lista de horários.")
            except ValueError:
                print("🤖 Entrada inválida. Por favor, digite um número correspondente ao horário.")
            print("-" * 50)
            continue

        # --- FLUXO 2: Usuário está escolhendo um ESPECIALISTA de uma lista numerada de sugestões ---
        elif contexto_sugestoes_pendentes and is_numeric_choice:
            try:
                escolha_idx = int(entrada_usuario) - 1
                if 0 <= escolha_idx < len(contexto_sugestoes_pendentes):
                    especialista_escolhido_tupla = contexto_sugestoes_pendentes[escolha_idx]
                    especialista_nome_mapa = normalizar_texto_geral(especialista_escolhido_tupla[0]) # Usar nome normalizado como chave

                    if especialista_nome_mapa in agenda:
                        print(f"🤖 Você escolheu {especialista_nome_mapa.capitalize()}.")
                        contexto_especialista_para_agendar = especialista_nome_mapa
                        contexto_horarios_oferecidos = mostrar_horarios_disponiveis_com_opcoes(especialista_nome_mapa)
                        if not contexto_horarios_oferecidos: # Nenhum horário disponível
                            contexto_especialista_para_agendar = None # Reset
                    else:
                        print(f"🤖 Desculpe, ainda não temos agenda para {especialista_nome_mapa.capitalize()}.")
                    contexto_sugestoes_pendentes = None # Limpa contexto de sugestão
                else:
                    print("🤖 Opção inválida. Por favor, escolha um número da lista de especialistas.")
            except ValueError:
                 print("🤖 Entrada inválida. Por favor, digite um número correspondente ao especialista.")
            print("-" * 50)
            continue
        elif contexto_sugestoes_pendentes and input_lower in ['não', 'nao', 'n', 'cancelar']:
            print("🤖 Entendido. Se precisar de outra coisa, é só chamar.")
            contexto_sugestoes_pendentes = None
            contexto_especialista_para_agendar = None
            contexto_horarios_oferecidos = None
            print("-" * 50)
            continue

        # --- FLUXO 3: Nova entrada do usuário (tentar agendamento direto ou sugestão) ---
        # Limpar contextos anteriores se não foram respondidos diretamente
        contexto_sugestoes_pendentes = None
        contexto_especialista_para_agendar = None
        contexto_horarios_oferecidos = None

        # Tenta extrair um pedido de agendamento direto
        esp_direto, dt_hr_direto = extrair_info_agendamento(entrada_usuario)

        if esp_direto and dt_hr_direto: # INTENÇÃO: AGENDAR CONSULTA DIRETAMENTE
            status_agenda = verificar_agenda(esp_direto, dt_hr_direto)
            if status_agenda == "disponível":
                nome = input(f"🤖 Horário disponível para {esp_direto.capitalize()} em {dt_hr_direto.strftime('%d/%m/%Y às %H:%M')}! Qual seu nome completo? ")
                if nome:
                    registrar_consulta(nome, esp_direto, dt_hr_direto)
                else:
                    print("🤖 Nome não fornecido. Agendamento cancelado.")
            else:
                print(f"🤖 Desculpe, o horário para {esp_direto.capitalize()} em {dt_hr_direto.strftime('%d/%m/%Y às %H:%M')} não está disponível.")
                contexto_especialista_para_agendar = esp_direto # Guarda para mostrar horários
                contexto_horarios_oferecidos = mostrar_horarios_disponiveis_com_opcoes(esp_direto)
                if not contexto_horarios_oferecidos:
                     contexto_especialista_para_agendar = None # Reset se não há opções

        else: # INTENÇÃO: SUGESTÃO DE ESPECIALISTA (ou não entendeu)
            sugestoes = sugerir_especialistas(entrada_usuario)
            if sugestoes:
                print("\n🤖 Com base na sua descrição, aqui estão algumas sugestões de especialistas:")
                contexto_sugestoes_pendentes = []
                for i, (especialista, pontuacao) in enumerate(sugestoes[:3]): # Mostrar até 3
                    print(f"   {i+1}. {especialista} (Relevância: {pontuacao:.1f})")
                    contexto_sugestoes_pendentes.append((especialista, pontuacao))
                
                if len(sugestoes) == 1 and normalizar_texto_geral(sugestoes[0][0]) in agenda:
                     # Se só uma sugestão e temos agenda, perguntar se quer marcar
                     especialista_sugerido_nome_mapa = normalizar_texto_geral(sugestoes[0][0])
                     print(f"🤖 Gostaria de ver os horários e marcar uma consulta com {especialista_sugerido_nome_mapa.capitalize()}? (Digite o número '1' ou 'não')")
                elif contexto_sugestoes_pendentes:
                    print("🤖 Digite o número do especialista que deseja consultar ou 'não' para nenhuma das opções.")
                else: # Caso raro, sugestoes existe mas contexto_sugestoes_pendentes ficou vazio
                     print("🤖 Não consegui encontrar um especialista adequado com base na sua descrição.")
                     contexto_sugestoes_pendentes = None


                # Adicionar Clínico Geral se não estiver nas top sugestões
                if not any(normalizar_texto_geral(esp_tupla[0]) == "clínico geral" for esp_tupla in contexto_sugestoes_pendentes if contexto_sugestoes_pendentes):
                    print("   Lembre-se: Um Clínico Geral também é uma boa opção para uma avaliação inicial.")
                
            else:
                print("🤖 Desculpe, não consegui entender claramente. Por favor, descreva seus sintomas ou peça para marcar uma consulta informando o especialista e o horário (ex: 'marcar cardiologista para amanhã 14h').")
        
        print("-" * 50)

if __name__ == "__main__":
    # Exemplo de como popular a agenda com mais horários para teste
    # (datas devem ser futuras em relação à data de execução)
    # Ex: hoje é 27/05/2025
    if "cardiologista" in agenda:
        agenda["cardiologista"]["2025-07-20 09:00"] = "disponível"
        agenda["cardiologista"]["2025-07-20 10:00"] = "disponível"
    if "dermatologista" in agenda:
         agenda["dermatologista"]["2025-07-22 14:00"] = "disponível"

    chatbot_hibrido()
