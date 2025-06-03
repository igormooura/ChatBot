from qdrant_client import QdrantClient, models # models contém PointStruct, VectorParams, Distance
from sentence_transformers import SentenceTransformer

# --- Configurações ---
QDRANT_HOST = "localhost"
QDRANT_HTTP_PORT = 6333
QDRANT_GRPC_PORT = 6334 # Porta gRPC que mapeamos no Docker
COLLECTION_NAME = "especialidades_medicas"
# Modelo do SentenceTransformer (gera vetores de dimensão 384)
EMBEDDING_MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'
VECTOR_SIZE = 384
DISTANCE_METRIC = models.Distance.COSINE

# Seu dicionário de especialistas e sintomas (do seu segundo script)
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

def main():
    # 1. Conectar ao Qdrant
    print(f"Conectando ao Qdrant (gRPC em {QDRANT_HOST}:{QDRANT_GRPC_PORT}, HTTP em {QDRANT_HOST}:{QDRANT_HTTP_PORT})...")
    client = QdrantClient(
        host=QDRANT_HOST,
        port=QDRANT_HTTP_PORT,    # Porta para API REST (HTTP)
        grpc_port=QDRANT_GRPC_PORT, # Porta para API gRPC
        prefer_grpc=True          # Instrui o cliente a preferir gRPC quando disponível
    )
    print("Cliente Qdrant inicializado!")

    # 2. Criar a coleção se ela não existir
    try:
        client.get_collection(collection_name=COLLECTION_NAME)
        print(f"Coleção '{COLLECTION_NAME}' já existe.")
    except Exception: # Se der erro, a coleção provavelmente não existe
        print(f"Coleção '{COLLECTION_NAME}' não encontrada. Criando...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=DISTANCE_METRIC)
        )
        print(f"Coleção '{COLLECTION_NAME}' criada com sucesso.")

    # 3. Carregar o modelo de embedding
    print(f"Carregando o modelo de embedding '{EMBEDDING_MODEL_NAME}'...")
    # Isso pode levar um tempo na primeira vez para baixar o modelo
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print("Modelo carregado.")

    # 4. Preparar e inserir os pontos (dados dos especialistas)
    points_to_upsert = []
    current_id = 0 # Usaremos IDs numéricos simples
    print("Preparando pontos para inserção...")
    for especialista, palavras_chave in ESPECIALISTAS_SINTOMAS.items():
        # Criar um texto descritivo para gerar o embedding
        # Concatenar o nome do especialista com suas palavras-chave
        texto_descritivo = f"{especialista}. Palavras-chave: {', '.join(palavras_chave)}."
        
        # Gerar o vetor (embedding)
        vector = model.encode(texto_descritivo).tolist()
        
        # Definir o payload (dados adicionais que queremos armazenar)
        payload = {
            "nome_especialista": especialista,
            "palavras_chave_originais": palavras_chave
            # Você pode adicionar mais campos aqui se quiser, ex: "descricao_detalhada", etc.
        }
        
        points_to_upsert.append(
            models.PointStruct(
                id=current_id,
                vector=vector,
                payload=payload
            )
        )
        current_id += 1
        print(f"  Ponto preparado para: {especialista}")

    # 5. Inserir os pontos na coleção no Qdrant
    if points_to_upsert:
        print(f"\nInserindo {len(points_to_upsert)} pontos na coleção '{COLLECTION_NAME}'...")
        # O `wait=True` faz a chamada esperar a operação ser concluída no servidor.
        client.upsert(collection_name=COLLECTION_NAME, points=points_to_upsert, wait=True)
        print("Pontos inseridos com sucesso!")
    else:
        print("Nenhum ponto para inserir.")

    # 6. Verificar a quantidade de pontos na coleção
    collection_info = client.get_collection(collection_name=COLLECTION_NAME)
    print(f"\nInformações da coleção '{COLLECTION_NAME}':")
    print(f"  Total de pontos: {collection_info.points_count}")
    print(f"  Status da coleção: {collection_info.status}")

    # Fechar a conexão
    client.close()
    print("\nProcesso concluído e conexão fechada.")

if __name__ == "__main__":
    main()