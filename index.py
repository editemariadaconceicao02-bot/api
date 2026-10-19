from flask import Flask, request
import requests
import os

app = Flask(__name__)

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("PHONE_ID")
GROQ_KEY = os.getenv("GROQ_KEY")

def perguntar_ia(texto):
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": f"Você é um assistente para casal, responda curto em português: {texto}"}],
                "max_tokens": 300
            },
            timeout=15
        )
        return r.json()['choices'][0]['message']['content']
    except Exception as e:
        print(e)
        return "Deu um erro aqui, tenta de novo :)"

@app.route("/api", methods=["GET"])
def verifica():
    # Meta verifica seu domínio
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == "meu_token_secreto_123":
        return challenge
    return "Token inválido", 403

@app.route("/api", methods=["POST"])
def recebe():
    data = request.json
    try:
        value = data['entry'][0]['changes'][0]['value']
        if 'messages' not in value:
            return "ok", 200
        
        mensagem = value['messages'][0]['text']['body']
        numero = value['messages'][0]['from']

        # Só responde se tiver @bot
        if "@bot" in mensagem.lower():
            resposta = perguntar_ia(mensagem)
            requests.post(
                f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages",
                headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"},
                json={
                    "messaging_product": "whatsapp",
                    "to": numero,
                    "type": "text",
                    "text": {"body": resposta}
                }
            )
    except Exception as e:
        print("Erro:", e)
    
    return "ok", 200
