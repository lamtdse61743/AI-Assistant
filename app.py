from flask import Flask, request, render_template, jsonify, session, url_for
from flask_session import Session
import requests
import os

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Static folder setup
app.static_folder = 'static'

# ✅ OpenRouter API Key (replace with your actual one if needed)
OPENROUTER_API_KEY = "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"

def generate_completion(messages):
    # 1. Try Chutes First
    chutes_api_keys = [
        "cpk_28e5e0309c094eb2984d7b2ba689dc37.069af37bc9e159da9822f8e74eb520d9.Q8F4RtOYdfPLmCxZV1ORc7ACtG66KCqK",
        "cpk_2303b6f00c0b4b4c8f6fbaa26441cee1.869dfa4d0621595582185c13022cec79.ZL9G9bhRmLjDRhiu2I0fXInXdJF56nPe",
        "cpk_7f975a65098d48c09d0700a1fc13e0f0.544fd3cea9b558138fc93c92084a4961.743aGHwCkroweZfwOkPOaaeBSJphVxSm"
        # Add more keys if rotating
    ]

    for chutes_key in chutes_api_keys:
        try:
            chutes_headers = {
                "Authorization": f"Bearer {chutes_key}",
                "Content-Type": "application/json"
            }
            chutes_payload = {
                "model": "deepseek-ai/DeepSeek-V3-0324",
                "messages": messages,
                "stream": False,
                "max_tokens": 1024,
                "temperature": 0.7
            }

            chutes_response = requests.post(
                "https://llm.chutes.ai/v1/chat/completions",
                headers=chutes_headers,
                json=chutes_payload
            )

            if chutes_response.status_code == 200:
                return "[Chutes] " + chutes_response.json()["choices"][0]["message"]["content"]

        except Exception as e:
            continue  # Try next key or fallback

    # 2. Fallback to OpenRouter
    try:
        openrouter_headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "Ask AI Assistant",
            "Content-Type": "application/json"
        }
        openrouter_payload = {
            "model": "deepseek/deepseek-chat-v3-0324:free",
            "messages": messages
        }

        openrouter_response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=openrouter_headers,
            json=openrouter_payload
        )

        openrouter_response.raise_for_status()
        return "[OpenRouter] " + openrouter_response.json()["choices"][0]["message"]["content"]

    except Exception as e:
        raise RuntimeError(f"❌ All APIs failed. Final error: {str(e)}")



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.form['prompt']

    if 'chat_history' not in session:
        session['chat_history'] = []

    session['chat_history'].append({"role": "user", "content": user_input})

    try:
        response_text = generate_completion(session['chat_history'])
    except requests.exceptions.HTTPError as e:
        response_text = f"⚠️ Error: {e.response.status_code} - {e.response.json().get('error', {}).get('message', str(e))}"
    except Exception as e:
        response_text = f"⚠️ Unexpected Error: {str(e)}"

    session['chat_history'].append({"role": "assistant", "content": response_text})
    session.modified = True

    return jsonify({'response': response_text})

@app.route('/clear', methods=['POST'])
def clear():
    session.pop('chat_history', None)
    return jsonify({'status': 'cleared'})

if __name__ == '__main__':
    app.run(debug=True)
