from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Render provides PORT environment variable
port = int(os.environ.get("PORT", 5000))

@app.route('/')
def home():
    return jsonify({
        "service": "AI Teacher 24/7",
        "status": "running",
        "host": "Render.com",
        "24/7": True
    })

@app.route('/api/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question', '')
    
    # Simple responses for now
    responses = {
        "hello": "Hello! I'm your AI Teacher running 24/7 on Render!",
        "what is ai": "AI is Artificial Intelligence - machines that can learn!",
        "what is python": "Python is a popular programming language!",
    }
    
    answer = responses.get(question.lower(), 
              f"I can teach you about: {question}. This is running 24/7 on Render!")
    
    return jsonify({"success": True, "answer": answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=False)
