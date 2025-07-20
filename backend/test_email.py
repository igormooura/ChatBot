# backend/test_email.py

import smtplib
import os
from dotenv import load_dotenv
from email.message import EmailMessage

# Carrega variáveis do .env
load_dotenv()

EMAIL_ADDRESS = os.getenv('MAIL_USERNAME')
EMAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
RECIPIENT_EMAIL = "ericksousasaraiva@gmail.com"  # Pode testar com o seu

if not all([EMAIL_ADDRESS, EMAIL_PASSWORD, RECIPIENT_EMAIL]):
    print("ERRO: Verifique MAIL_USERNAME, MAIL_PASSWORD e RECIPIENT_EMAIL.")
else:
    # === Teste com TLS (porta 587) ===
    try:
        print("--- Testando Conexão com TLS (porta 587) ---")
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as smtp:
            smtp.set_debuglevel(1)
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

            msg = EmailMessage()
            msg["Subject"] = "Teste de Conexão TLS (Porta 587)"
            msg["From"] = EMAIL_ADDRESS
            msg["To"] = RECIPIENT_EMAIL
            msg.set_content("Se você recebeu este e-mail, a conexão com TLS na porta 587 funcionou!")

            smtp.send_message(msg)
            print("\n✅ E-mail enviado com sucesso via TLS!")
    except Exception as e:
        print(f"\n❌ FALHA ao conectar com TLS: {e}")

    print("\n" + "="*50 + "\n")

    # === Teste com SSL (porta 465) ===
    try:
        print("--- Testando Conexão com SSL (porta 465) ---")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as smtp:
            smtp.set_debuglevel(1)
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

            msg = EmailMessage()
            msg["Subject"] = "Teste de Conexão SSL (Porta 465)"
            msg["From"] = EMAIL_ADDRESS
            msg["To"] = RECIPIENT_EMAIL
            msg.set_content("Se você recebeu este e-mail, a conexão com SSL na porta 465 funcionou!")

            smtp.send_message(msg)
            print("\n✅ E-mail enviado com sucesso via SSL!")
    except Exception as e:
        print(f"\n❌ FALHA ao conectar com SSL: {e}")
