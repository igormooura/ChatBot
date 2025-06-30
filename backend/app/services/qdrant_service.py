# backend/services/qdrant_service.py

from config import (
    qdrant_client, embedding_model, qdrant_ready, COLLECTION_NAME
)
from ..utils.normalizacao import normalizar_texto_geral

def sugerir_especialistas_qdrant(descricao_sintomas, top_k=3):
    if not qdrant_ready:
        print("DEBUG: Sistema Qdrant não está pronto.")
        return []
    if not descricao_sintomas:
        return []

    texto_para_embedding = normalizar_texto_geral(descricao_sintomas)
    try:
        vetor_sintomas = embedding_model.encode(texto_para_embedding).tolist()
        
        search_results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=vetor_sintomas,
            limit=top_k,
            with_payload=True
        )
        
        sugestoes = []
        if search_results:
            for hit in search_results:
                if hit.payload and hit.score is not None:
                    sugestoes.append((hit.payload.get("nome_especialista", "N/A"), hit.score))
        return sugestoes
    except Exception as e:
        print(f"ERRO ao buscar especialista no Qdrant: {e}")
        import traceback
        traceback.print_exc()
        return []