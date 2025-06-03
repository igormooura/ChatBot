import spacy
import re
import dateparser # Certifique-se de que está importado se for usado em extrair_info_agendamento
from datetime import datetime
# from collections import Counter # Counter não será mais necessário aqui

# --- QDRANT: Novas importações ---
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

# --- CONFIGURAÇÃO INICIAL ---

# Carrega o modelo de linguagem do spaCy
nlp = None # Inicializa nlp como None
try:
    nlp = spacy.load("pt_core_news_lg")
    print("Modelo Spacy 'pt_core_news_lg' carregado.")
except OSError:
    print("ALERTA: Modelo 'pt_core_news_lg' do Spacy não encontrado. "
          "Algumas funcionalidades de processamento de data/hora podem ser afetadas.")
    # Não vamos dar exit(), o chatbot pode tentar funcionar sem ele para a parte de Qdrant,
    # mas a extração de datas pode ser comprometida.

# --- QDRANT: Configurações ---
QDRANT_HOST = "localhost"
QDRANT_HTTP_PORT = 6333
QDRANT_GRPC_PORT = 6334
COLLECTION_NAME = "especialidades_medicas"
EMBEDDING_MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2' # Mesmo modelo usado para popular

# --- QDRANT: Inicialização do Cliente e Modelo (fazer uma vez) ---
qdrant_client = None
embedding_model = None
qdrant_ready = False # Flag para indicar se o Qdrant e o modelo de embedding estão prontos

try:
    print(f"Conectando ao Qdrant (gRPC em {QDRANT_HOST}:{QDRANT_GRPC_PORT}, HTTP em {QDRANT_HOST}:{QDRANT_HTTP_PORT})...")
    qdrant_client = QdrantClient(
        host=QDRANT_HOST,
        port=QDRANT_HTTP_PORT,
        grpc_port=QDRANT_GRPC_PORT,
        prefer_grpc=True
    )
    qdrant_client.get_collection(collection_name=COLLECTION_NAME) # Testa conexão e se a coleção existe
    print(f"Conectado com sucesso à coleção '{COLLECTION_NAME}' no Qdrant.")
    
    print(f"Carregando o modelo de embedding '{EMBEDDING_MODEL_NAME}'...")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print("Modelo de embedding carregado.")
    qdrant_ready = True # Marcar como pronto se tudo ocorreu bem
except Exception as e:
    print(f"ERRO CRÍTICO QDRANT: Não foi possível conectar ao Qdrant ou carregar o modelo de embedding. Detalhes: {e}")
    print("O chatbot não poderá fornecer sugestões de especialistas.")
    # qdrant_client e embedding_model permanecem None, qdrant_ready permanece False


# O DICIONÁRIO ESPECIALISTAS_SINTOMAS FOI REMOVIDO DESTE SCRIPT.
# Ele agora deve estar apenas no seu script de inserção de dados do Qdrant.

# Simulação de banco de dados de AGENDA e consultas (mantido como no seu original)
agenda = {
    "cardiologista": {"2025-07-15 15:00": "disponível", "2025-07-15 16:00": "ocupado", "2025-07-16 10:00": "disponível"},
    "dermatologista": {"2025-07-17 09:00": "disponível", "2025-07-17 10:00": "disponível"},
    "ortopedista": {"2025-07-18 11:00": "disponível"},
    "clínico geral": {"2025-07-15 08:00": "disponível", "2025-07-15 09:00": "ocupado"}
}
consultas_registradas = []

# --- FUNÇÕES AUXILIARES ---

# A função normalizar_texto_sugestao não é mais necessária se não houver fallback de palavras-chave.
# A normalizar_texto_geral ainda é usada por extrair_info_agendamento.
def normalizar_texto_geral(texto):
    texto = texto.lower()
    # Simplificando as substituições de regex para uma linha por caractere para clareza
    texto = re.sub(r'[áàâãä]', 'a', texto)
    texto = re.sub(r'[éèêë]', 'e', texto)
    texto = re.sub(r'[íìîï]', 'i', texto)
    texto = re.sub(r'[óòôõö]', 'o', texto)
    texto = re.sub(r'[úùûü]', 'u', texto)
    texto = re.sub(r'[ç]', 'c', texto)
    return texto.strip()

# --- QDRANT: Função de sugestão usando Qdrant ---
def sugerir_especialistas_qdrant(descricao_sintomas_usuario, top_k=3):
    # Verifica se o cliente Qdrant e o modelo de embedding estão prontos
    if not qdrant_ready or not qdrant_client or not embedding_model:
        # Não imprime erro aqui, pois já foi avisado na inicialização
        return [] 

    if not descricao_sintomas_usuario:
        return []

    # O texto do usuário é usado diretamente para o embedding,
    # pois os modelos SentenceTransformer geralmente lidam bem com texto "cru".
    texto_para_embedding = descricao_sintomas_usuario.lower()

    try:
        vetor_sintomas_usuario = embedding_model.encode(texto_para_embedding).tolist()
        
        search_results_obj = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=vetor_sintomas_usuario,
            limit=top_k,
            with_payload=True 
        )
        
        sugestoes = []
        # Acessa os resultados através do atributo 'points' do objeto QueryResponse
        if search_results_obj and hasattr(search_results_obj, 'points') and search_results_obj.points:
            actual_hits = search_results_obj.points

            for hit in actual_hits: # 'hit' aqui é um objeto ScoredPoint
                nome_especialista = None
                score = None

                if hit.payload: # Checa se o payload existe
                    nome_especialista = hit.payload.get("nome_especialista")
                
                score = hit.score # score é um atributo direto do ScoredPoint
                
                if nome_especialista and score is not None:                                  
                    sugestoes.append((nome_especialista, score))       
        return sugestoes

    except Exception as e:
        print(f"ERRO ao buscar especialista no Qdrant: {e}")
        # import traceback # Descomente para debug completo, se necessário
        # traceback.print_exc() 
        return [] # Retorna lista vazia em caso de erro na busca

# A FUNÇÃO SUGERIR_ESPECIALISTAS_FALLBACK FOI REMOVIDA.

# Funções de agendamento (extrair_info_agendamento, etc.) permanecem as mesmas
def extrair_info_agendamento(texto):
    texto_norm_geral = normalizar_texto_geral(texto)
    especialidade_encontrada = None
    data_hora = None
    for esp_nome_mapa in agenda.keys():
        if esp_nome_mapa in texto_norm_geral:
            especialidade_encontrada = esp_nome_mapa
            texto_para_data = texto_norm_geral.replace(esp_nome_mapa, "").strip()
            # Garante que dateparser seja importado e usado
            if dateparser:
                data_hora = dateparser.parse(texto_para_data, languages=['pt'], settings={'PREFER_DATES_FROM': 'future', 'DATE_ORDER': 'DMY'})
            else:
                print("ALERTA: dateparser não está disponível. Extração de data falhará.")
            break
    return especialidade_encontrada, data_hora

def mostrar_horarios_disponiveis_com_opcoes(especialidade_nome_mapa):
    print(f"🤖 Estes são os horários disponíveis para {especialidade_nome_mapa.capitalize()}:")
    horarios_raw_disponiveis = [
        hora_str for hora_str, status in agenda.get(especialidade_nome_mapa, {}).items()
        if status == 'disponível'
    ]
    horarios_raw_disponiveis.sort() 
    if horarios_raw_disponiveis:
        for i, horario_str in enumerate(horarios_raw_disponiveis):
            dt_obj = datetime.strptime(horario_str, "%Y-%m-%d %H:%M")
            print(f"   {i+1}. {dt_obj.strftime('%d/%m/%Y às %H:%M')}")
    else:
        print("   - Desculpe, não há horários disponíveis no momento para este especialista.")
    return horarios_raw_disponiveis

def verificar_agenda(especialidade_nome_mapa, data_hora_obj):
    if especialidade_nome_mapa and data_hora_obj:
        data_formatada_str = data_hora_obj.strftime("%Y-%m-%d %H:%M")
        return agenda.get(especialidade_nome_mapa, {}).get(data_formatada_str, "não disponível")
    return "não disponível"

def registrar_consulta(nome_paciente, especialidade_nome_mapa, data_hora_obj):
    data_formatada_str = data_hora_obj.strftime("%Y-%m-%d %H:%M")
    # Garante que a especialidade exista na agenda antes de tentar acessar
    if especialidade_nome_mapa not in agenda:
        agenda[especialidade_nome_mapa] = {} # Cria se não existir
        
    agenda[especialidade_nome_mapa][data_formatada_str] = "ocupado"
    consultas_registradas.append({
        "nome": nome_paciente,
        "especialidade": especialidade_nome_mapa.capitalize(),
        "data_hora": data_formatada_str
    })
    print(f"✅ Consulta confirmada com sucesso para {nome_paciente} com {especialidade_nome_mapa.capitalize()} em {data_hora_obj.strftime('%d/%m/%Y às %H:%M')}!")

# --- CHATBOT PRINCIPAL (Lógica Híbrida Aprimorada) ---
def chatbot_hibrido():
    # Verifica se o Spacy foi carregado, pois algumas funções podem depender dele (como dateparser implicitamente)
    if nlp is None:
        print("AVISO: Modelo Spacy 'pt_core_news_lg' não carregado. A funcionalidade de extração de datas pode ser limitada.")
        # Você pode decidir se quer continuar ou não. Por ora, vamos continuar.

    print("🤖 Olá! Sou seu assistente de saúde.")
    print("   Você pode descrever seus sintomas para eu sugerir um especialista,")
    print("   ou pode pedir diretamente para marcar uma consulta (ex: 'marcar dermatologista amanhã às 10h').")
    print("   Digite 'sair' a qualquer momento para encerrar.")
    print("-" * 50)

    contexto_sugestoes_pendentes = None
    contexto_especialista_para_agendar = None
    contexto_horarios_oferecidos = None

    while True:
        entrada_usuario = input("Você: ").strip()
        if entrada_usuario.lower() in ["sair", "encerrar", "tchau", "exit"]:
            print("🤖 Até logo! Cuide-se.")
            break

        input_lower = entrada_usuario.lower()
        is_numeric_choice = entrada_usuario.isdigit()

        # FLUXO 1: Escolhendo HORÁRIO
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
                    contexto_especialista_para_agendar = None; contexto_horarios_oferecidos = None; contexto_sugestoes_pendentes = None
                else:
                    print("🤖 Opção inválida. Por favor, escolha um número da lista de horários.")
            except ValueError:
                print("🤖 Entrada inválida. Por favor, digite um número correspondente ao horário.")
            print("-" * 50); continue

        # FLUXO 2: Escolhendo ESPECIALISTA
        elif contexto_sugestoes_pendentes and is_numeric_choice:
            try:
                escolha_idx = int(entrada_usuario) - 1
                if 0 <= escolha_idx < len(contexto_sugestoes_pendentes):
                    especialista_escolhido_tupla = contexto_sugestoes_pendentes[escolha_idx]
                    especialista_nome_mapa = normalizar_texto_geral(especialista_escolhido_tupla[0])
                    if especialista_nome_mapa in agenda:
                        print(f"🤖 Você escolheu {especialista_nome_mapa.capitalize()}.")
                        contexto_especialista_para_agendar = especialista_nome_mapa
                        contexto_horarios_oferecidos = mostrar_horarios_disponiveis_com_opcoes(especialista_nome_mapa)
                        if not contexto_horarios_oferecidos: contexto_especialista_para_agendar = None
                    else:
                        print(f"🤖 Desculpe, ainda não temos agenda para {especialista_nome_mapa.capitalize()}.")
                    contexto_sugestoes_pendentes = None
                else:
                    print("🤖 Opção inválida. Por favor, escolha um número da lista de especialistas.")
            except ValueError:
                print("🤖 Entrada inválida. Por favor, digite um número correspondente ao especialista.")
            print("-" * 50); continue
        elif contexto_sugestoes_pendentes and input_lower in ['não', 'nao', 'n', 'cancelar']:
            print("🤖 Entendido. Se precisar de outra coisa, é só chamar.")
            contexto_sugestoes_pendentes = None; contexto_especialista_para_agendar = None; contexto_horarios_oferecidos = None
            print("-" * 50); continue

        # FLUXO 3: Nova entrada
        contexto_sugestoes_pendentes = None; contexto_especialista_para_agendar = None; contexto_horarios_oferecidos = None
        esp_direto, dt_hr_direto = extrair_info_agendamento(entrada_usuario)

        if esp_direto and dt_hr_direto: # Tenta agendamento direto
            status_agenda = verificar_agenda(esp_direto, dt_hr_direto)
            if status_agenda == "disponível":
                nome = input(f"🤖 Horário disponível para {esp_direto.capitalize()} em {dt_hr_direto.strftime('%d/%m/%Y às %H:%M')}! Qual seu nome completo? ")
                if nome: registrar_consulta(nome, esp_direto, dt_hr_direto)
                else: print("🤖 Nome não fornecido. Agendamento cancelado.")
            else:
                print(f"🤖 Desculpe, o horário para {esp_direto.capitalize()} em {dt_hr_direto.strftime('%d/%m/%Y às %H:%M')} não está disponível.")
                contexto_especialista_para_agendar = esp_direto
                contexto_horarios_oferecidos = mostrar_horarios_disponiveis_com_opcoes(esp_direto)
                if not contexto_horarios_oferecidos: contexto_especialista_para_agendar = None
        else: # Se não for agendamento direto, tenta sugestão de especialista
            if qdrant_ready: # Só tenta sugestão do Qdrant se ele estiver pronto
                sugestoes = sugerir_especialistas_qdrant(entrada_usuario)
            else:
                sugestoes = [] # Define como vazio se Qdrant não está pronto
                print("🤖 Desculpe, meu sistema de sugestão de especialistas está temporariamente indisponível.")

            if sugestoes:
                print("\n🤖 Com base na sua descrição, aqui estão algumas sugestões de especialistas:")
                contexto_sugestoes_pendentes = []
                for i, (especialista, pontuacao) in enumerate(sugestoes[:3]):
                    print(f"   {i+1}. {especialista} (Similaridade: {pontuacao:.2f})")
                    contexto_sugestoes_pendentes.append((especialista, pontuacao))
                
                if len(sugestoes) == 1 and normalizar_texto_geral(sugestoes[0][0]) in agenda:
                    especialista_sugerido_nome_mapa = normalizar_texto_geral(sugestoes[0][0])
                    print(f"🤖 Gostaria de ver os horários e marcar uma consulta com {especialista_sugerido_nome_mapa.capitalize()}? (Digite o número '1' ou 'não')")
                elif contexto_sugestoes_pendentes:
                    print("🤖 Digite o número do especialista que deseja consultar ou 'não' para nenhuma das opções.")
                else: # Sugestões retornou algo, mas o contexto ficou vazio (raro)
                    print("🤖 Não consegui encontrar um especialista adequado com base na sua descrição.")
                    contexto_sugestoes_pendentes = None
                
                if not any(normalizar_texto_geral(esp_tupla[0]) == "clínico geral" for esp_tupla in contexto_sugestoes_pendentes if contexto_sugestoes_pendentes):
                    print("   Lembre-se: Um Clínico Geral também é uma boa opção para uma avaliação inicial.")
            elif qdrant_ready: # Se qdrant_ready é True, mas não houve sugestões (lista vazia)
                print("🤖 Não consegui encontrar um especialista específico com base na sua descrição no momento.")
                print("   Tente descrever seus sintomas com mais detalhes ou considere procurar um Clínico Geral.")
            # Se qdrant_ready é False, a mensagem de indisponibilidade já foi dada.
        
        print("-" * 50)

if __name__ == "__main__":
    if "cardiologista" in agenda:
        agenda["cardiologista"]["2025-07-20 09:00"] = "disponível"
        agenda["cardiologista"]["2025-07-20 10:00"] = "disponível"
    if "dermatologista" in agenda:
        agenda["dermatologista"]["2025-07-22 14:00"] = "disponível"
    
    chatbot_hibrido()