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

# ✅ Function to call OpenRouter API
def generate_completion(messages):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Ask AI Assistant",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "messages": messages
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

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
