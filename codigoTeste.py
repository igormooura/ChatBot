import spacy
import re
from collections import Counter

# Carrega o modelo de linguagem em português do spaCy
# Se você não tiver o modelo, instale-o com: python -m spacy download pt_core_news_sm
try:
    nlp = spacy.load("pt_core_news_lg")
except OSError:
    print("Modelo 'pt_core_news_lg' não encontrado. "
          "Por favor, instale-o executando: python -m spacy download pt_core_news_lg")
    exit()

# Definição de especialidades e palavras-chave associadas
# Esta lista pode ser expandida e refinada
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

# Função para normalizar o texto
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

# Função para sugerir especialista
def sugerir_especialista(descricao_sintomas):
    """
    Analisa a descrição dos sintomas e sugere um especialista.
    Retorna uma lista de tuplas (especialista, pontuação) ordenada pela pontuação.
    """
    if not descricao_sintomas:
        return []

    texto_normalizado = normalizar_texto(descricao_sintomas)
    doc = nlp(texto_normalizado)

    # Extrai tokens (palavras) relevantes da descrição
    tokens_usuario = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct and token.is_alpha]
    
    # Contagem de palavras-chave por especialista
    contagem_especialistas = Counter()

    for especialista, palavras_chave in ESPECIALISTAS_SINTOMAS.items():
        palavras_chave_normalizadas = [normalizar_texto(chave) for chave in palavras_chave]
        score = 0
        # Verifica a presença de palavras-chave simples e compostas
        for chave_norm in palavras_chave_normalizadas:
            if chave_norm in texto_normalizado: # Verifica se a string da chave está contida
                score += texto_normalizado.count(chave_norm) # Conta ocorrências da substring
                # Adiciona mais peso para palavras-chave mais longas (mais específicas)
                score += len(chave_norm.split()) -1


        # Adiciona pontos por tokens individuais que correspondem
        # (menos preciso que a correspondência de frase/substring, mas útil)
        # for token_usr in tokens_usuario:
        #     for palavra_chave_especialista in palavras_chave_normalizadas:
        #         if token_usr in palavra_chave_especialista.split(): # Se o token faz parte de uma palavra chave
        #             score += 0.5 # Menor peso para tokens soltos

        if score > 0:
            contagem_especialistas[especialista] = score
            
    sugestoes_ordenadas = contagem_especialistas.most_common()

    return sugestoes_ordenadas

# Função principal do chatbot
def chatbot_especialista():
    """Função principal que executa o loop do chatbot."""
    print("Olá! Sou seu assistente virtual de saúde.")
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

        sugestoes = sugerir_especialista(entrada_usuario)

        if sugestoes:
            print("\nChatbot: Com base na sua descrição, aqui estão algumas sugestões de especialistas:")
            for i, (especialista, pontuacao) in enumerate(sugestoes):
                if i < 3 : # Mostrar até 3 sugestões principais
                    print(f"  - {especialista} (Relevância: {pontuacao:.2f})")
            
            if not any(esp == "Clínico Geral" for esp, _ in sugestoes[:3]) and len(sugestoes) > 0 :
                 print("  - Clínico Geral (para uma avaliação inicial mais ampla)")

            print("\nLembre-se: esta é apenas uma sugestão e não substitui uma consulta médica.")
            print("Um Clínico Geral também é uma boa opção para uma primeira avaliação.")
        else:
            print("Chatbot: Não consegui identificar um especialista específico com base na sua descrição.")
            print("Tente descrever seus sintomas com mais detalhes ou considere procurar um Clínico Geral para uma avaliação inicial.")
        
        print("-" * 30)
        print("Chatbot: Posso ajudar com mais alguma coisa? (Descreva novos sintomas ou digite 'sair')")


if __name__ == "__main__":
    chatbot_especialista()
