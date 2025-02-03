from flask import Blueprint, request, jsonify
from ollama import Client
import subprocess
import platform
import threading
import time

ai_api = Blueprint('ai_api', __name__)
client = Client(host='http://localhost:11434')

active_requests = 0
active_requests_lock = threading.Lock()

def close_server_if_inactive():
    """Close the Ollama server if no active requests"""
    global active_requests
    time.sleep(2) 
    with active_requests_lock:
        if active_requests == 0:
            if platform.system() == "Windows":
                subprocess.run(['taskkill', '/F', '/IM', 'ollama_llama_server.exe'], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
            else:
                subprocess.run(['pkill', 'ollama'], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)

@ai_api.route('/generate', methods=['POST'])
def generate_response():
    global active_requests
    
    try:
        with active_requests_lock:
            active_requests += 1
        
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Prompt is required'}), 400

        prompt = data['prompt']
        
        message = ""
        for chunk in client.generate(
            model='deepseek-r1:1.5b',
            prompt=prompt,
            stream=True
        ):
            if chunk.get('done'):
                break
            message += chunk.get('response', '')

        response = {
            'success': True,
            'response': message
        }

        with active_requests_lock:
            active_requests -= 1
            if active_requests == 0:
                threading.Thread(target=close_server_if_inactive).start()
                
        return jsonify(response)

    except Exception as e:
        with active_requests_lock:
            active_requests -= 1
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500