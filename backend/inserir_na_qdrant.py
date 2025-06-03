from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

# --- Configurações ---
QDRANT_HOST = "localhost"
QDRANT_HTTP_PORT = 6333 # Certifique-se que é a porta HTTP correta do seu Qdrant
QDRANT_GRPC_PORT = 6334 # Certifique-se que é a porta gRPC correta
COLLECTION_NAME = "especialidades_medicas"
EMBEDDING_MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'
VECTOR_SIZE = 384 # Deve corresponder à saída do EMBEDDING_MODEL_NAME
DISTANCE_METRIC = models.Distance.COSINE

# Copie EXATAMENTE o mesmo dicionário ESPECIALISTAS_SINTOMAS do seu script do chatbot aqui
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

def popular_qdrant():
    print(f"Iniciando script para popular o Qdrant...")
    try:
        print(f"Conectando ao Qdrant (gRPC em {QDRANT_HOST}:{QDRANT_GRPC_PORT}, HTTP em {QDRANT_HOST}:{QDRANT_HTTP_PORT})...")
        client = QdrantClient(
            host=QDRANT_HOST,
            port=QDRANT_HTTP_PORT,
            grpc_port=QDRANT_GRPC_PORT,
            prefer_grpc=True
        )
        print("Cliente Qdrant inicializado!")

        # Verificar se a coleção existe, se não, criar
        try:
            client.get_collection(collection_name=COLLECTION_NAME)
            print(f"Coleção '{COLLECTION_NAME}' já existe. Para repopular, delete-a primeiro ou use 'recreate_collection'.")
            # Se quiser sempre recriar (CUIDADO: apaga dados existentes):
            # print(f"Recriando coleção '{COLLECTION_NAME}'...")
            # client.recreate_collection(
            #     collection_name=COLLECTION_NAME,
            #     vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=DISTANCE_METRIC)
            # )
            # print(f"Coleção '{COLLECTION_NAME}' recriada.")
        except Exception: # Se der erro, a coleção provavelmente não existe
            print(f"Coleção '{COLLECTION_NAME}' não encontrada. Criando...")
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=DISTANCE_METRIC)
            )
            print(f"Coleção '{COLLECTION_NAME}' criada com sucesso.")

        print(f"Carregando o modelo de embedding '{EMBEDDING_MODEL_NAME}'...")
        model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print("Modelo de embedding carregado.")

        points_to_upsert = []
        current_id = 0 
        print("Preparando pontos para inserção...")
        for especialista, palavras_chave in ESPECIALISTAS_SINTOMAS.items():
            texto_descritivo = f"{especialista}. Palavras-chave: {', '.join(palavras_chave)}."
            vector = model.encode(texto_descritivo).tolist()
            payload = {
                "nome_especialista": especialista,
                "palavras_chave_originais": palavras_chave
            }
            points_to_upsert.append(
                models.PointStruct(id=current_id, vector=vector, payload=payload)
            )
            print(f"  Ponto preparado para ID {current_id}: {especialista}")
            current_id += 1
        
        if points_to_upsert:
            print(f"\nInserindo/atualizando {len(points_to_upsert)} pontos na coleção '{COLLECTION_NAME}'...")
            client.upsert(collection_name=COLLECTION_NAME, points=points_to_upsert, wait=True)
            print("Pontos inseridos/atualizados com sucesso!")
        else:
            print("Nenhum ponto para inserir.")

        collection_info = client.get_collection(collection_name=COLLECTION_NAME)
        print(f"\nInformações da coleção '{COLLECTION_NAME}':")
        print(f"  Total de pontos: {collection_info.points_count}")
        print(f"  Status da coleção: {collection_info.status}")

        client.close()
        print("\nProcesso de população concluído e conexão fechada.")

    except Exception as e:
        print(f"ERRO GERAL no script de população: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    popular_qdrant()