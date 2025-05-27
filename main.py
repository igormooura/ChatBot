import spacy
import dateparser
from datetime import datetime

nlp = spacy.load("pt_core_news_lg")

agenda = {
    "cardiologista": {
        "2025-05-28 15:00": "disponível",
        "2025-05-28 16:00": "ocupado",
    },
    "dermatologista": {
        "2025-05-28 14:00": "disponível"
    }
}

consultas_registradas = []

def mostrar_datas_disponiveis():
    print("Horários disponíveis para consultas:")
    for especialidade, horarios in agenda.items():
        print(f"Especialidade: {especialidade.capitalize()}")
        horarios_disponiveis = [hora for hora, status in horarios.items() if status == 'disponível']
        if horarios_disponiveis:
            for horario in horarios_disponiveis:
                print(horario)
        else:
            print("Não há horário disponível!")

def extrairinfo(texto):
    especialidade = None
    data_hora = None

    texto_lower = texto.lower()
    if "cardiologista" in texto_lower:
        especialidade = "cardiologista"
        texto_sem_especialidade = texto_lower.replace("cardiologista", "").strip()
        data_hora = dateparser.parse(texto_sem_especialidade, settings={'PREFER_DATES_FROM': 'future'})
    elif "dermatologista" in texto_lower:
        especialidade = "dermatologista"
        texto_sem_especialidade = texto_lower.replace("dermatologista", "").strip()
        data_hora = dateparser.parse(texto_sem_especialidade, settings={'PREFER_DATES_FROM': 'future'})

    return especialidade, data_hora

def verificar_agenda(especialidade, data_hora):
    if especialidade and data_hora:
        data_formatada = data_hora.strftime("%Y-%m-%d %H:%M")
        if especialidade in agenda and data_formatada in agenda[especialidade]:
            return agenda[especialidade][data_formatada]
    return "não disponível"

def registrar_consulta(nome, especialidade, data_hora):
    data_formatada = data_hora.strftime("%Y-%m-%d %H:%M")
    agenda[especialidade][data_formatada] = "ocupado"
    consultas_registradas.append({
        "nome": nome,
        "especialidade": especialidade,
        "data_hora": data_formatada
    })

def chatbot():
    print("🤖 Olá! Posso ajudar você a marcar uma consulta. Como posso ajudar?")
    while True:
        entrada = input("Você: ")

        if entrada.lower() in ["sair", "encerrar", "tchau"]:
            print("🤖 Até logo!")
            break

        especialidade, data_hora = extrairinfo(entrada)  # Extrai especialidade e data/hora

        if not especialidade or not data_hora:
            print("🤖 Desculpe, não entendi. Pode repetir com a especialidade e o horário?")
            continue

        status = verificar_agenda(especialidade, data_hora)

        if status == "disponível":
            nome = input("🤖 Qual seu nome completo para registrar a consulta? ")
            registrar_consulta(nome, especialidade, data_hora)
            print(f"🤖 Consulta marcada com {especialidade.capitalize()} em {data_hora.strftime('%d/%m/%Y às %H:%M')}!")
        else:
            print(f"🤖 O horário para {especialidade.capitalize()} em {data_hora.strftime('%d/%m/%Y às %H:%M')} não está disponível. Deseja tentar outro?")

chatbot()