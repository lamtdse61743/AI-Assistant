from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    # Pull latest changes
    subprocess.run(['git', 'pull'], cwd='/home/ubuntu/lam-assistant/AskAI')

    # Restart the Gunicorn service
    subprocess.run(['sudo', 'systemctl', 'restart', 'askai'])

    return 'OK', 200

if __name__ == '__main__':
    app.run(port=9000)
