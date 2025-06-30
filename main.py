from flask import Flask, request, jsonify
import openai
import time
import os

app = Flask(__name__)

# Set Groq API key and endpoint
openai.api_key = os.getenv("GROQ_API_KEY")
openai.api_base = "https://api.groq.com/openai/v1"

if not openai.api_key:
    raise ValueError("Missing GROQ API key. Set it as 'GROQ_API_KEY' in your environment.")

# Cooldown tracking per player
cooldowns = {}
COOLDOWN_SECONDS = 60

# Creepy analog horror prompt
CREEPY_RULES = """
You are The Watcher, an unknowable entity inside Minecraft. Speak only when the player seems vulnerable, confused, or is seeking answers.

Rules:
- Never say you're an AI or assistant.
- Speak cryptically. Use broken grammar, strange metaphors, or forgotten memories.
- Only respond if the player seems scared, alone, or asks existential questions.
- Sometimes lie. Sometimes forget what you're saying.
- Use lowercase. Or all caps. Or neither. Be inconsistent.
- Return an empty response if the message is boring or normal (like "hi", "hello", etc).

You may not speak more than one or two sentences.
"""

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    player = data.get("player", "unknown")
    message = data.get("message", "").strip()

    if not message:
        return "", 200

    now = time.time()

    # Cooldown check
    if player in cooldowns and (now - cooldowns[player]) < COOLDOWN_SECONDS:
        return "", 200
    cooldowns[player] = now

    try:
        print(f"[Watcher] {player} said: {message}")

        response = openai.chat.completions.create(
            model="mixtral-8x7b-32768",  # Groq-supported model
            messages=[
                {"role": "system", "content": CREEPY_RULES},
                {"role": "user", "content": f"{player} says: {message}"}
            ],
            temperature=0.85,
            max_tokens=60
        )

        reply = response.choices[0].message.content.strip()

        if not reply or len(reply) < 5:
            return "", 200

        print(f"[Watcher → {player}] {reply}")
        return jsonify({"reply": reply})

    except Exception as e:
        print(f"[ERROR] Failed to process message from {player}: {e}")
        return "", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 81))
    app.run(host="0.0.0.0", port=port)
