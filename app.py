from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json

app = Flask(__name__)
CORS(app)  # Allow Android app to connect

# 🔑 YOUR OPENROUTER API KEY (already included)
OPENROUTER_API_KEY = "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"

# AI Model configuration
MODEL = "meta-llama/llama-3.2-3b-instruct"  # Free fast model
FALLBACK_MODEL = "huggingfaceh4/zephyr-7b-beta"  # Alternative if first fails

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'deployed': True,
        'provider': 'Render.com + OpenRouter',
        'model': MODEL,
        'message': '✅ AI Teacher Backend is LIVE and ready!',
        'endpoints': {
            'ask': '/api/ask (POST)',
            'health': '/api/health (GET)',
            'test': '/api/test (GET)'
        }
    })

@app.route('/api/ask', methods=['POST'])
def ask_ai():
    """Main AI endpoint - uses OpenRouter API"""
    try:
        data = request.json
        
        if not data or 'question' not in data:
            return jsonify({'error': 'No question provided'}), 400
        
        question = data['question'].strip()
        
        if not question:
            return jsonify({'error': 'Empty question'}), 400
        
        print(f"🤔 Processing question: {question[:50]}...")
        
        # Try primary model first
        response = call_openrouter(question, MODEL)
        
        if response.get('error'):
            # Fallback to secondary model
            print("🔄 Trying fallback model...")
            response = call_openrouter(question, FALLBACK_MODEL)
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Error in ask_ai: {str(e)}")
        return jsonify({
            'answer': f"Sorry, I encountered an error. Please try again. Error: {str(e)[:100]}",
            'error': str(e),
            'fallback': True
        }), 500

def call_openrouter(question, model_name):
    """Call OpenRouter API with the specified model"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://ai-teacher-sepq.onrender.com",
        "X-Title": "AI Teacher"
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "system", 
                "content": """You are AI Teacher - a helpful, patient, and educational assistant. 
                You explain concepts clearly with examples. Keep responses concise but complete.
                Format responses with proper paragraphs. If you don't know something, admit it."""
            },
            {
                "role": "user", 
                "content": question
            }
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract the AI response
            if 'choices' in result and len(result['choices']) > 0:
                answer = result['choices'][0]['message']['content']
                
                return {
                    'answer': answer.strip(),
                    'model': model_name,
                    'tokens_used': result.get('usage', {}).get('total_tokens', 0),
                    'provider': 'OpenRouter',
                    'cloud': True,
                    'success': True
                }
            else:
                return {
                    'answer': "I received an unexpected response format from the AI service.",
                    'error': 'Invalid response format',
                    'success': False
                }
                
        else:
            error_msg = f"API Error {response.status_code}"
            try:
                error_detail = response.json().get('error', {}).get('message', response.text[:200])
                error_msg = f"{error_msg}: {error_detail}"
            except:
                error_msg = f"{error_msg}: {response.text[:200]}"
            
            return {
                'answer': f"AI service is temporarily unavailable. Please try again in a moment.",
                'error': error_msg,
                'success': False
            }
            
    except requests.exceptions.Timeout:
        return {
            'answer': "The AI is taking too long to respond. Please try a simpler question or try again later.",
            'error': 'Request timeout',
            'success': False
        }
    except Exception as e:
        return {
            'answer': f"Network error: {str(e)[:100]}",
            'error': str(e),
            'success': False
        }

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint - returns simple response"""
    return jsonify({
        'message': '🚀 AI Teacher Cloud Backend is WORKING!',
        'status': 'operational',
        'url': 'https://ai-teacher-sepq.onrender.com',
        'model': MODEL,
        'instructions': 'Send POST request to /api/ask with {"question": "your question"}',
        'example': {
            'curl': 'curl -X POST https://ai-teacher-sepq.onrender.com/api/ask -H "Content-Type: application/json" -d \'{"question":"Hello"}\''
        }
    })

@app.route('/api/simple', methods=['POST'])
def simple_ask():
    """Simplified endpoint for quick testing"""
    try:
        question = request.json.get('question', '')
        if not question:
            return jsonify({'answer': 'Please provide a question'})
        
        # Direct response without API call (for testing)
        return jsonify({
            'answer': f'Hello! You asked: "{question}". This is AI Teacher running on Render cloud with OpenRouter API.',
            'simple': True,
            'timestamp': 'now'
        })
    except:
        return jsonify({'answer': 'Test response from cloud backend'})

@app.route('/')
def home():
    """Home page with interactive testing"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Teacher - Cloud Backend</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
                color: #333;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 { color: #4a5568; margin-bottom: 20px; }
            .status { 
                background: #48bb78; 
                color: white;
                padding: 10px 20px;
                border-radius: 25px;
                display: inline-block;
                margin-bottom: 30px;
            }
            .endpoint {
                background: #f7fafc;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
            }
            .test-area {
                margin: 40px 0;
            }
            input[type="text"] {
                width: 100%;
                padding: 15px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 16px;
                margin: 10px 0;
            }
            button {
                background: #667eea;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                transition: background 0.3s;
            }
            button:hover { background: #5a67d8; }
            .response {
                background: #f0fff4;
                border: 1px solid #9ae6b4;
                border-radius: 8px;
                padding: 20px;
                margin-top: 20px;
                white-space: pre-wrap;
            }
            .url {
                background: #edf2f7;
                padding: 15px;
                border-radius: 8px;
                font-family: monospace;
                word-break: break-all;
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 AI Teacher Cloud Backend</h1>
            <div class="status">✅ DEPLOYED & RUNNING</div>
            
            <p>Your backend is successfully deployed to Render.com with OpenRouter AI integration.</p>
            
            <div class="url">
                <strong>Base URL:</strong><br>
                https://ai-teacher-sepq.onrender.com
            </div>
            
            <h3>📱 Android App Configuration:</h3>
            <p>Update your Android app with this URL:</p>
            <div class="endpoint">
                <code>BASE_URL = "https://ai-teacher-sepq.onrender.com"</code>
            </div>
            
            <h3>🔗 Available Endpoints:</h3>
            <div class="endpoint">
                <strong>GET</strong> <code>/api/health</code> - Check backend status
            </div>
            <div class="endpoint">
                <strong>POST</strong> <code>/api/ask</code> - Ask AI questions (main endpoint)
            </div>
            <div class="endpoint">
                <strong>GET</strong> <code>/api/test</code> - Test endpoint
            </div>
            
            <div class="test-area">
                <h3>🚀 Test Your AI Backend:</h3>
                <input type="text" id="question" placeholder="Ask a question..." value="What is machine learning?">
                <button onclick="askAI()">Ask AI Teacher</button>
                
                <div id="loading" style="display:none; margin:20px 0;">
                    <div style="display:flex; align-items:center;">
                        <div style="width:20px; height:20px; border:3px solid #e2e8f0; border-top-color:#667eea; border-radius:50%; animation:spin 1s linear infinite; margin-right:10px;"></div>
                        AI is thinking...
                    </div>
                </div>
                
                <div id="response" class="response"></div>
            </div>
            
            <div style="margin-top:40px; padding-top:20px; border-top:1px solid #e2e8f0;">
                <small>
                    <strong>Next Steps:</strong><br>
                    1. Update Android app with above URL<br>
                    2. Test all endpoints<br>
                    3. Build and publish to Google Play
                </small>
            </div>
        </div>
        
        <script>
            async function askAI() {
                const question = document.getElementById('question').value;
                const loading = document.getElementById('loading');
                const responseDiv = document.getElementById('response');
                
                if (!question) {
                    responseDiv.innerHTML = 'Please enter a question';
                    return;
                }
                
                // Show loading
                loading.style.display = 'block';
                responseDiv.innerHTML = '';
                
                try {
                    const response = await fetch('/api/ask', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ question: question })
                    });
                    
                    const data = await response.json();
                    
                    if (data.error) {
                        responseDiv.innerHTML = `<strong>Error:</strong> ${data.error}<br><br>${data.answer || ''}`;
                    } else {
                        responseDiv.innerHTML = `<strong>🤖 AI Response:</strong><br><br>${data.answer}`;
                        if (data.model) {
                            responseDiv.innerHTML += `<br><br><small>Model: ${data.model}</small>`;
                        }
                    }
                } catch (error) {
                    responseDiv.innerHTML = `<strong>Connection Error:</strong> ${error.message}`;
                } finally {
                    loading.style.display = 'none';
                }
            }
        </script>
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </body>
    </html>
    '''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 Starting AI Teacher Cloud Backend on port {port}")
    print(f"🌍 Your app will be available at: https://ai-teacher-sepq.onrender.com")
    print(f"🤖 Using model: {MODEL}")
    print(f"🔑 API Key configured: {'Yes' if OPENROUTER_API_KEY else 'No'}")
    app.run(host='0.0.0.0', port=port, debug=False)
