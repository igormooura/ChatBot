# backend/app/utils/normalizacao.py
import re

def normalizar_texto_geral(texto):
    if not isinstance(texto, str):
        return ""

    # --- LINHA ADICIONADA: A SOLUÇÃO ---
    # Remove o caractere nulo (0x00) que causa erros no PostgreSQL.
    texto = texto.replace('\x00', '')
    # ------------------------------------

    texto = texto.lower()
    texto = re.sub(r'[áàâãä]', 'a', texto)
    texto = re.sub(r'[éèêë]', 'e', texto)
    texto = re.sub(r'[íìîï]', 'i', texto)
    texto = re.sub(r'[óòôõö]', 'o', texto)
    texto = re.sub(r'[úùûü]', 'u', texto)
    texto = re.sub(r'[ç]', 'c', texto)
    return texto.strip()