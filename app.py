from flask import Flask, request, render_template, jsonify, session, url_for
from flask_session import Session
from openai import OpenAI
import os
import requests

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

<<<<<<< HEAD
# Static folder setup for logo
app.static_folder = 'static'

# OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

=======
# Static folder setup
app.static_folder = 'static'

# ✅ OpenRouter API Key (replace with your new one if needed)
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
    response.raise_for_status()  # Raises 401/403/500 as Python exceptions
    return response.json()["choices"][0]["message"]["content"]

# ✅ Routes
>>>>>>> 76d95b5 (Initial commit from server)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.form['prompt']

<<<<<<< HEAD
    # Create a new chat history if needed
    if 'chat_history' not in session:
        session['chat_history'] = []

    # Append user message
    session['chat_history'].append({"role": "user", "content": user_input})

    # Get completion
    completion = client.chat.completions.create(
        model="deepseek/deepseek-chat-v3-0324:free",
        messages=session['chat_history'],
        extra_headers={
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "Ask AI"
        }
    )

    response_text = completion.choices[0].message.content
=======
    if 'chat_history' not in session:
        session['chat_history'] = []

    session['chat_history'].append({"role": "user", "content": user_input})

    try:
        response_text = generate_completion(session['chat_history'])
    except requests.exceptions.HTTPError as e:
        response_text = f"⚠️ Error: {e.response.status_code} - {e.response.json().get('error', {}).get('message', str(e))}"
    except Exception as e:
        response_text = f"⚠️ Unexpected Error: {str(e)}"

>>>>>>> 76d95b5 (Initial commit from server)
    session['chat_history'].append({"role": "assistant", "content": response_text})
    session.modified = True

    return jsonify({'response': response_text})

@app.route('/clear', methods=['POST'])
def clear():
    session.pop('chat_history', None)
    return jsonify({'status': 'cleared'})

<<<<<<< HEAD
=======
# ✅ Run app
>>>>>>> 76d95b5 (Initial commit from server)
if __name__ == '__main__':
    app.run(debug=True)
