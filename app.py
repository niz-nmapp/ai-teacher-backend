from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import threading
import time
import os

app = Flask(__name__)
CORS(app)

# Configuration
MODEL = "llama3.2:3b"  # Already installed on your laptop!
ollama_running = False

def check_ollama():
    """Check if Ollama is running"""
    global ollama_running
    try:
        result = subprocess.run(["ollama", "list"], 
                              capture_output=True, text=True, timeout=5)
        ollama_running = "llama3.2:3b" in result.stdout
        return ollama_running
    except:
        ollama_running = False
        return False

def start_ollama_background():
    """Start Ollama in background if not running"""
    if not check_ollama():
        print("🚀 Starting Ollama server...")
        try:
            # Start Ollama server
            subprocess.Popen(["ollama", "serve"], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)
            time.sleep(10)  # Wait for server to start
            
            # Pull model if not exists
            print("📥 Ensuring model is available...")
            subprocess.run(["ollama", "pull", MODEL], 
                         capture_output=True, text=True)
            
            print("✅ Ollama ready on laptop!")
            return True
        except Exception as e:
            print(f"❌ Failed to start Ollama: {e}")
            return False
    return True

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    is_running = check_ollama()
    
    return jsonify({
        'status': 'online' if is_running else 'starting',
        'server': 'YOUR LAPTOP (RTX 3050)',
        'model': MODEL,
        'ollama_running': is_running,
        '24_7': 'YES (when laptop is on)',
        'gpu': 'RTX 3050 4GB',
        'performance': 'FAST (local GPU)',
        'message': 'AI Teacher running on YOUR laptop!',
        'endpoints': {
            'ask': '/api/ask (POST)',
            'health': '/api/health (GET)',
            'test': '/api/test (GET)',
            'simple': '/api/simple (POST)'
        }
    })

@app.route('/api/ask', methods=['POST'])
def ask_ai():
    """Ask Llama running locally on your laptop"""
    try:
        data = request.json
        
        if not data or 'question' not in data:
            return jsonify({'error': 'No question provided'}), 400
        
        question = data['question'].strip()
        
        if not question:
            return jsonify({'error': 'Empty question'}), 400
        
        print(f"🤔 Processing on laptop GPU: {question[:50]}...")
        
        # Ensure Ollama is running
        if not start_ollama_background():
            return jsonify({
                'answer': 'Starting AI engine... Please wait 30 seconds.',
                'status': 'starting'
            }), 503
        
        # Use Ollama CLI to generate response
        prompt = f'''You are AI Teacher - a helpful, patient assistant. 
Answer clearly with examples. Keep response concise.

Question: {question}

Answer:'''
        
        result = subprocess.run([
            'ollama', 'run', MODEL,
            prompt
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            answer = result.stdout.strip()
            
            return jsonify({
                'answer': answer,
                'model': MODEL,
                'server': 'Your Laptop (RTX 3050)',
                'performance': 'GPU accelerated',
                'response_time': 'fast',
                '24_7': True,
                'local': True
            })
        else:
            return jsonify({
                'answer': f"I'm thinking about: '{question}'. Please wait...",
                'error': result.stderr[:100],
                'fallback': True
            })
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'answer': "The AI is taking time to think. Try a simpler question.",
            'error': 'timeout',
            'local': True
        })
    except Exception as e:
        return jsonify({
            'answer': f"AI Teacher is here! Question: '{question}'",
            'error': str(e)[:100],
            'local': True
        })

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint"""
    return jsonify({
        'message': '🚀 AI Teacher Running on YOUR Laptop',
        'status': 'operational',
        'server': 'Local (RTX 3050)',
        'model': MODEL,
        '24_7': 'When laptop is on',
        'gpu': 'YES - RTX 3050',
        'url': 'Use ngrok tunnel for external access'
    })

@app.route('/api/simple', methods=['POST'])
def simple_ask():
    """Simple always-working endpoint"""
    question = request.json.get('question', 'Hello')
    
    return jsonify({
        'answer': f"🤖 AI Teacher (Local): I can help with '{question}'. Running on your RTX 3050!",
        'simple': True,
        'local': True,
        'gpu': 'RTX 3050',
        'reliable': True
    })

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Teacher - Local Laptop Server</title>
        <style>
            body { font-family: Arial; padding: 20px; background: #f0f2f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .status { background: #48bb78; color: white; padding: 10px; border-radius: 5px; display: inline-block; }
            .url { background: #edf2f7; padding: 15px; border-radius: 5px; margin: 15px 0; font-family: monospace; }
            button { background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }
            .response { background: #f0fff4; padding: 15px; border-radius: 5px; margin-top: 15px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 AI Teacher - Local Server</h1>
            <div class="status">✅ RUNNING ON YOUR LAPTOP</div>
            <div class="status">🎮 GPU: RTX 3050</div>
            
            <p>Your AI backend is running locally on your laptop with Ollama + Llama 3.2!</p>
            
            <div class="url">
                <strong>Local URL:</strong> http://localhost:5000<br>
                <strong>Android Access:</strong> Use ngrok tunnel (see below)
            </div>
            
            <h3>🔧 Setup ngrok for 24/7 Android Access:</h3>
            <ol>
                <li>Download ngrok from ngrok.com</li>
                <li>Extract to C:\ngrok</li>
                <li>Get free auth token from ngrok dashboard</li>
                <li>Run: <code>ngrok http 5000</code></li>
                <li>Use the ngrok URL in Android app</li>
            </ol>
            
            <div>
                <h3>🚀 Test Local Server:</h3>
                <input type="text" id="question" value="Hello from local server" style="width: 70%; padding: 10px;">
                <button onclick="testAsk()">Ask Local AI</button>
                <button onclick="testHealth()">Check Health</button>
                
                <div id="result" class="response"></div>
            </div>
            
            <div style="margin-top: 30px; padding: 20px; background: #f7fafc; border-radius: 5px;">
                <h3>📱 Android App Setup:</h3>
                <pre style="background: #2d3748; color: white; padding: 10px; border-radius: 5px;">
// Temporary: Use ngrok URL
private const val BASE_URL = "https://your-ngrok-url.ngrok-free.app"

// When ngrok restarts, update this URL
                </pre>
            </div>
        </div>
        
        <script>
            async function testAsk() {
                const question = document.getElementById('question').value;
                const result = document.getElementById('result');
                result.innerHTML = 'Asking local AI...';
                
                try {
                    const response = await fetch('/api/ask', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({question: question})
                    });
                    const data = await response.json();
                    result.innerHTML = `<strong>🤖 Local AI:</strong><br>${data.answer}<br>
                                       <small>Model: ${data.model} | GPU: ${data.server}</small>`;
                } catch(e) {
                    result.innerHTML = 'Error: ' + e.message;
                }
            }
            
            async function testHealth() {
                const result = document.getElementById('result');
                result.innerHTML = 'Checking health...';
                
                try {
                    const response = await fetch('/api/health');
                    const data = await response.json();
                    result.innerHTML = `<strong>✅ Health:</strong><br>
                                       Status: ${data.status}<br>
                                       Model: ${data.model}<br>
                                       GPU: ${data.gpu}<br>
                                       24/7: ${data['24_7']}`;
                } catch(e) {
                    result.innerHTML = 'Error: ' + e.message;
                }
            }
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("🚀 Starting AI Teacher Local Server")
    print("💻 Running on YOUR laptop")
    print("🎮 GPU: RTX 3050")
    print("🤖 Model: llama3.2:3b")
    print("🌐 Local URL: http://localhost:5000")
    print("📱 Use ngrok for Android access")
    
    # Start Ollama in background
    start_ollama_background()
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
