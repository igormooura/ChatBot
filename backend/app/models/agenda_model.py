

from datetime import datetime, time
from ..utils.normalizacao import normalizar_texto_geral 


agenda = {
    "cardiologista": {
        "2025-06-29 10:00": "disponível", "2025-06-29 11:00": "disponível", "2025-06-30 15:00": "disponível",
    },
    "dermatologista": {
        "2025-07-01 09:00": "disponível", "2025-07-02 14:00": "disponível",
    },
    "ortopedista": {
        "2025-06-30 11:00": "disponível", "2025-07-03 14:00": "disponível",
    },
    "clinico geral": {
        "2025-06-29 08:00": "disponível", "2025-06-30 08:00": "disponível",
    },
}

consultas_registradas = []

def get_horarios_por_especialista(nome_especialista):
    """Retorna todos os horários de um especialista, disponíveis ou não."""
    nome_normalizado = normalizar_texto_geral(nome_especialista)
    return agenda.get(nome_normalizado, {})

def filtrar_agenda_disponivel(info_pedido):
    """Filtra a agenda com base nos critérios extraídos (especialista, data, período)."""
    especialista = info_pedido.get("especialista")
    if not especialista:
        return []

    data_desejada_str = info_pedido.get("data_base")
    periodo_dia = info_pedido.get("periodo_dia")
    
    data_desejada = datetime.strptime(data_desejada_str, "%Y-%m-%d") if data_desejada_str else None

    horarios_do_especialista = get_horarios_por_especialista(especialista)
    horarios_filtrados = []

    for horario_str, status in horarios_do_especialista.items():
        if status == "disponível":
            horario_dt = datetime.strptime(horario_str, "%Y-%m-%d %H:%M")

            if data_desejada and horario_dt.date() != data_desejada.date():
                continue

            if periodo_dia:
                if periodo_dia == "manha" and not (time(0, 0) <= horario_dt.time() < time(12, 0)):
                    continue
                if periodo_dia == "tarde" and not (time(12, 0) <= horario_dt.time() < time(18, 0)):
                    continue
                if periodo_dia == "noite" and not (time(18, 0) <= horario_dt.time() <= time(23, 59)):
                    continue
            
            horarios_filtrados.append(horario_str)

    horarios_filtrados.sort()
    return horarios_filtrados

def registrar_consulta_model(nome_paciente, especialidade, data_hora_str):
    """Marca uma consulta como 'ocupada' na agenda e a registra."""
    esp_normalizado = normalizar_texto_geral(especialidade)
    
    if esp_normalizado in agenda and data_hora_str in agenda[esp_normalizado]:
        if agenda[esp_normalizado][data_hora_str] == "disponível":
            agenda[esp_normalizado][data_hora_str] = "ocupado"
            consultas_registradas.append({
                "nome": nome_paciente, 
                "especialidade": especialidade, 
                "data_hora": data_hora_str
            })
            return True
    return False