from flask import Flask, request, render_template, jsonify, session, url_for
from flask_session import Session
from openai import OpenAI
import os

app = Flask(__name__)

# Secret key for sessions
app.secret_key = 'super-secret-key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Static folder setup for logo
app.static_folder = 'static'

# OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.form['prompt']

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
    session['chat_history'].append({"role": "assistant", "content": response_text})
    session.modified = True

    return jsonify({'response': response_text})

@app.route('/clear', methods=['POST'])
def clear():
    session.pop('chat_history', None)
    return jsonify({'status': 'cleared'})

if __name__ == '__main__':
    app.run(debug=True)
