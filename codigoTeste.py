import spacy
import re # Mantemos re para a função normalizar_texto, caso queira usá-la
# from collections import Counter # Counter não será mais necessário aqui

# Novas importações
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

# --- Configurações do Qdrant e Modelo de Embedding ---
QDRANT_HOST = "localhost"
QDRANT_HTTP_PORT = 6333
QDRANT_GRPC_PORT = 6334
COLLECTION_NAME = "especialidades_medicas"
EMBEDDING_MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2' # Mesmo modelo usado para popular

# Carregar o modelo de linguagem em português do spaCy (opcional para esta versão, mas pode ser útil para outras coisas)
try:
    nlp_spacy = spacy.load("pt_core_news_lg")
    print("Modelo Spacy 'pt_core_news_lg' carregado.")
except OSError:
    print("Modelo Spacy 'pt_core_news_lg' não encontrado. "
          "Algumas funcionalidades avançadas de NLP podem não estar disponíveis.")
    nlp_spacy = None # Define como None se não puder carregar

# --- Inicialização do Cliente Qdrant e Modelo SentenceTransformer (fazer uma vez) ---
try:
    print(f"Conectando ao Qdrant (gRPC em {QDRANT_HOST}:{QDRANT_GRPC_PORT}, HTTP em {QDRANT_HOST}:{QDRANT_HTTP_PORT})...")
    qdrant_client = QdrantClient(
        host=QDRANT_HOST,
        port=QDRANT_HTTP_PORT,
        grpc_port=QDRANT_GRPC_PORT,
        prefer_grpc=True
    )
    print("Cliente Qdrant inicializado!")
    # Testar conexão básica e se a coleção existe
    qdrant_client.get_collection(collection_name=COLLECTION_NAME)
    print(f"Conectado com sucesso à coleção '{COLLECTION_NAME}' no Qdrant.")

except Exception as e:
    print(f"ERRO: Não foi possível conectar ao Qdrant ou à coleção '{COLLECTION_NAME}'. Verifique se o Qdrant está rodando. Detalhes: {e}")
    qdrant_client = None # Define como None se não puder conectar

try:
    if qdrant_client: # Só carrega o modelo de embedding se o Qdrant estiver acessível
        print(f"Carregando o modelo de embedding '{EMBEDDING_MODEL_NAME}'...")
        embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print("Modelo de embedding carregado.")
    else:
        embedding_model = None
        print("Modelo de embedding não carregado devido a falha na conexão com Qdrant.")
except Exception as e:
    print(f"ERRO: Não foi possível carregar o modelo de embedding SentenceTransformer. Detalhes: {e}")
    embedding_model = None


# A Definição de ESPECIALISTAS_SINTOMAS não é mais necessária aqui,
# pois esses dados já estão no Qdrant.

# Função para normalizar o texto (pode ser útil para pré-processar a entrada do usuário antes do embedding, opcional)
def normalizar_texto(texto):
    """Converte o texto para minúsculas, remove acentos e caracteres especiais."""
    texto = texto.lower()
    texto = re.sub(r'[áàâãä]', 'a', texto)
    texto = re.sub(r'[éèêë]', 'e', texto)
    texto = re.sub(r'[íìîï]', 'i', texto)
    texto = re.sub(r'[óòôõö]', 'o', texto)
    texto = re.sub(r'[úùûü]', 'u', texto)
    texto = re.sub(r'[ç]', 'c', texto)
    texto = re.sub(r'[^a-z0-9\s]', '', texto) # Remove pontuação e outros caracteres
    texto = texto.strip()
    return texto

# Nova Função para sugerir especialista usando Qdrant

def sugerir_especialista_qdrant(descricao_sintomas_usuario, top_k=3):
    if not qdrant_client or not embedding_model:
        print("ERRO: Cliente Qdrant ou modelo de embedding não inicializado corretamente.")
        return []
    if not descricao_sintomas_usuario:
        # print("Debug: Descrição de sintomas vazia.") # Pode remover este debug
        return []

    texto_para_embedding = descricao_sintomas_usuario 
    # print(f"Debug: Texto para embedding: '{texto_para_embedding}'") # Pode remover este debug

    try:
        vetor_sintomas_usuario = embedding_model.encode(texto_para_embedding).tolist()
        # print(f"Debug: Buscando no Qdrant com vetor de {len(vetor_sintomas_usuario)} dimensões.") # Pode remover

        search_results_obj = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=vetor_sintomas_usuario,
            limit=top_k,
            with_payload=True 
        )
        
        sugestoes = []
        
        # Verifica se o objeto de resposta existe e se o atributo 'points' contém algo
        if search_results_obj and hasattr(search_results_obj, 'points') and search_results_obj.points:
            actual_hits = search_results_obj.points # <<< CORREÇÃO PRINCIPAL AQUI!

            # print(f"Debug: Foram encontrados {len(actual_hits)} hits.") # Debug opcional

            for i, hit in enumerate(actual_hits): # Agora 'hit' deve ser um ScoredPoint
                # print(f"Debug Loop (iteração {i}): Tipo de hit: {type(hit)}, Conteúdo de hit: {hit}") # Debug opcional
                
                nome_especialista = None
                score = None

                # Acessando payload e score (hit é um objeto ScoredPoint)
                if hit.payload: # Verifica se payload não é None
                    nome_especialista = hit.payload.get("nome_especialista") 
                
                score = hit.score # score é um atributo direto do ScoredPoint
                
                if nome_especialista and score is not None:                                  
                    sugestoes.append((nome_especialista, score))       
                else:
                    print(f"Debug Loop (iteração {i}): Não foi possível obter nome_especialista ou score do hit: {hit}")

            # print(f"Debug: Encontradas {len(sugestoes)} sugestões válidas no Qdrant.") # Debug opcional
        else:
            # print("Debug: Nenhum resultado (search_results_obj.points) retornado pela busca no Qdrant.") # Debug opcional
            if search_results_obj:
                 # Se quiser ver o objeto de resposta mesmo quando .points está vazio:
                 # print(f"Debug: Conteúdo do search_results_obj (caso .points esteja vazio): {str(search_results_obj)[:200]}")
                 pass

        return sugestoes

    except Exception as e:
        print(f"Erro ao buscar especialista no Qdrant: {e}")
        import traceback 
        traceback.print_exc() 
        return []

# (O resto do seu script chatbot_especialista() e a chamada if __name__ == "__main__": permanecem os mesmos)
# Agora, a mensagem do chatbot para o usuário deve mostrar as sugestões!

# Função principal do chatbot (adaptada)
def chatbot_especialista():
    """Função principal que executa o loop do chatbot."""
    if not qdrant_client or not embedding_model:
        print("Chatbot não pode iniciar. Cliente Qdrant ou modelo de embedding falhou na inicialização.")
        return

    print("\nOlá! Sou seu assistente virtual de saúde (versão Qdrant).") # Mensagem atualizada
    print("Posso te ajudar a identificar qual especialista médico você talvez precise consultar.")
    print("Por favor, descreva seus sintomas ou o que você está sentindo.")
    print("Digite 'sair' a qualquer momento para encerrar.")
    print("-" * 30)

    while True:
        entrada_usuario = input("Você: ")
        if entrada_usuario.lower() == 'sair':
            print("Chatbot: Até logo! Cuide-se.")
            break

        if not entrada_usuario.strip():
            print("Chatbot: Por favor, descreva seus sintomas para que eu possa ajudar.")
            continue

        # Chama a nova função de sugestão baseada em Qdrant
        sugestoes = sugerir_especialista_qdrant(entrada_usuario)

        if sugestoes:
            print("\nChatbot: Com base na sua descrição, aqui estão algumas sugestões de especialistas:")
            for i, (especialista, pontuacao) in enumerate(sugestoes):
                # O score do Qdrant (similaridade de cosseno) varia, geralmente entre 0 e 1 para vetores normalizados.
                # Quanto maior, mais similar.
                print(f"  - {especialista} (Similaridade: {pontuacao:.2f})")
            
            # Lógica para sugerir Clínico Geral pode ser mantida se desejado,
            # ou você pode adicionar "Clínico Geral" aos dados no Qdrant com palavras-chave genéricas.
            # Se "Clínico Geral" já está no Qdrant, ele pode aparecer naturalmente nas sugestões.
            # Verificando se o Clínico Geral já foi sugerido para evitar redundância:
            ja_sugeriu_clinico = any(esp.lower() == "clínico geral" for esp, _ in sugestoes)
            if not ja_sugeriu_clinico:
                 # Se quiser sempre adicionar como uma opção:
                 print("  - Clínico Geral (para uma avaliação inicial mais ampla, se as sugestões acima não parecerem adequadas)")


            print("\nLembre-se: esta é apenas uma sugestão e não substitui uma consulta médica.")
        else:
            print("Chatbot: Não consegui identificar um especialista específico com base na sua descrição.")
            print("Tente descrever seus sintomas com mais detalhes ou considere procurar um Clínico Geral para uma avaliação inicial.")
        
        print("-" * 30)
        print("Chatbot: Posso ajudar com mais alguma coisa? (Descreva novos sintomas ou digite 'sair')")


if __name__ == "__main__":
    # Verifica se os componentes essenciais foram carregados antes de iniciar o chatbot
    if qdrant_client and embedding_model:
        chatbot_especialista()
    else:
        print("Finalizando devido a erro na inicialização dos componentes necessários (Qdrant/Modelo de Embedding).")