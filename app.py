"""
AI TEACHER - FIXED VERSION
Proper session handling and storage
"""

import os
import sys
import time
import json
import uuid
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pyttsx3
import requests
import subprocess

# ==================== CONFIGURATION ====================
class Config:
    PORT = 5000
    HOST = '0.0.0.0'
    
    # Paths
    BASE_DIR = Path(__file__).parent
    STATIC_DIR = BASE_DIR / "static"
    AUDIO_DIR = STATIC_DIR / "audios"
    VIDEO_DIR = STATIC_DIR / "videos"
    FACE_DIR = STATIC_DIR / "input_photos"
    
    # Services
    LLAMA_URL = "http://127.0.0.1:11434/api/generate"
    LLAMA_MODEL = "llama3.2:3b"
    LLAMA_TIMEOUT = 30
    
    # Wav2Lip
    WAV2LIP_DIR = BASE_DIR / "Wav2Lip"

# Create directories
for d in [Config.AUDIO_DIR, Config.VIDEO_DIR, Config.FACE_DIR]:
    d.mkdir(exist_ok=True, parents=True)

# ==================== STARTUP MESSAGE ====================
print("=" * 70)
print("🤖 AI TEACHER - WORKING BACKEND")
print("=" * 70)

# ==================== FLASK APP ====================
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ==================== GLOBAL STORAGE ====================
# Use dictionary for session storage (in-memory)
sessions = {}
session_lock = threading.Lock()

# ==================== SYSTEM INIT ====================
print("🔍 Initializing components...")

# TTS Engine
try:
    tts_engine = pyttsx3.init()
    voices = tts_engine.getProperty('voices')
    for voice in voices:
        if 'david' in voice.name.lower():
            tts_engine.setProperty('voice', voice.id)
            print(f"🎤 Voice: {voice.name}")
            break
    tts_engine.setProperty('rate', 165)
    tts_engine.setProperty('volume', 1.0)
    TTS_READY = True
    print("✅ TTS: Ready")
except Exception as e:
    print(f"❌ TTS: Failed - {e}")
    TTS_READY = False
    tts_engine = None

# Check LLaMA
try:
    response = requests.get("http://127.0.0.1:11434", timeout=5)
    LLAMA_READY = response.status_code == 200
    print("✅ LLaMA: Connected" if LLAMA_READY else "❌ LLaMA: Not connected")
except:
    LLAMA_READY = False
    print("❌ LLaMA: Not connected")

# Check Wav2Lip
FACE_VIDEO = Config.FACE_DIR / "face.mp4"
WAV2LIP_READY = FACE_VIDEO.exists() and (Config.WAV2LIP_DIR / "inference.py").exists()
if FACE_VIDEO.exists():
    print("✅ Face video: Found")
else:
    print("⚠️ Face video: Not found")

print("=" * 70)

# ==================== AI FUNCTIONS ====================
def get_llama_answer(question):
    """Get answer from LLaMA"""
    try:
        prompt = f"""Please provide a detailed 5-7 line explanation about: {question}

Make it educational and easy to understand:"""
        
        response = requests.post(
            Config.LLAMA_URL,
            json={
                "model": Config.LLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 300,
                    "top_p": 0.9
                }
            },
            timeout=Config.LLAMA_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("response", "").strip()
            
            if answer and len(answer) > 50:
                return answer
    
    except Exception as e:
        print(f"LLaMA error: {e}")
    
    # Fallback answer
    return f"""Detailed explanation about {question}:

1. This topic involves important concepts worth understanding.
2. Core principles explain how it functions in practice.
3. Real-world applications demonstrate its relevance.
4. Learning this provides valuable insights.
5. Key mechanisms drive its effectiveness.
6. Further study can deepen understanding.
7. This overview serves as a solid foundation.

Hope this helps!"""

def generate_audio_background(text, session_id):
    """Generate audio in background"""
    if not TTS_READY:
        return
    
    try:
        audio_file = Config.AUDIO_DIR / f"audio_{session_id}.wav"
        
        # Clean text
        clean_text = text[:500].replace('\n', ' ')
        
        tts_engine.save_to_file(clean_text, str(audio_file))
        tts_engine.runAndWait()
        
        if audio_file.exists():
            # Update session
            with session_lock:
                if session_id in sessions:
                    sessions[session_id]['audio_file'] = f"audio_{session_id}.wav"
                    sessions[session_id]['audio_ready'] = True
            
            print(f"🔊 Audio generated: {session_id}")
            
            # Convert for Wav2Lip
            convert_audio(audio_file)
            
            # Start video generation
            if WAV2LIP_READY:
                threading.Thread(
                    target=generate_video_background,
                    args=(session_id,),
                    daemon=True
                ).start()
    
    except Exception as e:
        print(f"Audio error: {e}")

def generate_video_background(session_id):
    """Generate video in background"""
    try:
        with session_lock:
            if session_id not in sessions or not sessions[session_id].get('audio_ready'):
                return
            
            audio_file = sessions[session_id]['audio_file']
        
        audio_path = Config.AUDIO_DIR / audio_file
        
        if not audio_path.exists():
            return
        
        output_file = Config.VIDEO_DIR / f"video_{session_id}.mp4"
        
        # Run Wav2Lip
        original_dir = os.getcwd()
        os.chdir(str(Config.WAV2LIP_DIR))
        
        cmd = [
            sys.executable, "inference.py",
            "--checkpoint_path", "checkpoints/wav2lip_gan.pth",
            "--face", str(FACE_VIDEO),
            "--audio", str(audio_path),
            "--outfile", str(output_file),
            "--pads", "0", "10", "0", "0",
            "--nosmooth"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        os.chdir(original_dir)
        
        if result.returncode == 0 and output_file.exists():
            # Update session
            with session_lock:
                if session_id in sessions:
                    sessions[session_id]['video_file'] = f"video_{session_id}.mp4"
                    sessions[session_id]['video_ready'] = True
            
            print(f"🎬 Video generated: {session_id}")
    
    except Exception as e:
        print(f"Video error: {e}")

def convert_audio(audio_file):
    """Convert audio for Wav2Lip"""
    try:
        temp_file = Config.AUDIO_DIR / f"temp_{audio_file.stem}.wav"
        cmd = [
            "ffmpeg", "-y", "-i", str(audio_file),
            "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            str(temp_file)
        ]
        
        result = subprocess.run(cmd, capture_output=True, timeout=10)
        
        if result.returncode == 0 and temp_file.exists():
            audio_file.unlink()
            temp_file.rename(audio_file)
    
    except Exception as e:
        print(f"Audio convert warning: {e}")

# ==================== ROUTES ====================
@app.route('/')
def home():
    return jsonify({
        "service": "AI Teacher API",
        "status": "running",
        "sessions": len(sessions),
        "components": {
            "llama": LLAMA_READY,
            "tts": TTS_READY,
            "wav2lip": WAV2LIP_READY
        }
    })

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Ask a question"""
    try:
        data = request.get_json() or {}
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"success": False, "error": "Question required"}), 400
        
        # Create session
        session_id = str(uuid.uuid4())[:8]
        
        print(f"\n🎯 Question: {question[:50]}...")
        
        # Get answer
        start_time = time.time()
        answer = get_llama_answer(question)
        elapsed = time.time() - start_time
        
        print(f"✅ Answer in {elapsed:.2f}s")
        
        # Store session
        with session_lock:
            sessions[session_id] = {
                'question': question,
                'answer': answer,
                'created': datetime.now().isoformat(),
                'audio_ready': False,
                'video_ready': False,
                'audio_file': None,
                'video_file': None
            }
        
        # Start audio generation in background
        if TTS_READY:
            threading.Thread(
                target=generate_audio_background,
                args=(answer, session_id),
                daemon=True
            ).start()
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "question": question,
            "answer": answer,
            "response_time": f"{elapsed:.2f}s",
            "background": {
                "audio": "processing" if TTS_READY else "disabled",
                "video": "queued" if WAV2LIP_READY else "disabled"
            }
        })
    
    except Exception as e:
        print(f"API error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/status/<session_id>', methods=['GET'])
def get_status(session_id):
    """Get session status - FIXED VERSION"""
    with session_lock:
        if session_id not in sessions:
            return jsonify({"success": False, "error": "Session not found"}), 404
        
        session = sessions[session_id].copy()  # Create a copy
    
    response = {
        "success": True,
        "session_id": session_id,
        "question": session['question'],
        "answer": session['answer'],
        "audio_ready": session.get('audio_ready', False),
        "video_ready": session.get('video_ready', False)
    }
    
    if session.get('audio_ready') and session.get('audio_file'):
        response['audio'] = {
            "file": session['audio_file'],
            "url": f"/api/audio/{session['audio_file']}"
        }
    
    if session.get('video_ready') and session.get('video_file'):
        response['video'] = {
            "file": session['video_file'],
            "url": f"/api/video/{session['video_file']}"
        }
    
    return jsonify(response)

@app.route('/api/audio/<filename>', methods=['GET'])
def get_audio(filename):
    """Serve audio file"""
    try:
        return send_from_directory(str(Config.AUDIO_DIR), filename)
    except:
        return jsonify({"error": "Audio not found"}), 404

@app.route('/api/video/<filename>', methods=['GET'])
def get_video(filename):
    """Serve video file"""
    try:
        return send_from_directory(str(Config.VIDEO_DIR), filename)
    except:
        return jsonify({"error": "Video not found"}), 404

# ==================== CLEANUP ====================
def cleanup_sessions():
    """Clean old sessions every hour"""
    while True:
        time.sleep(3600)
        try:
            with session_lock:
                to_delete = []
                cutoff = datetime.now().timestamp() - 86400  # 24 hours
                
                for session_id, session in sessions.items():
                    created = datetime.fromisoformat(session['created']).timestamp()
                    if created < cutoff:
                        to_delete.append(session_id)
                
                for session_id in to_delete:
                    del sessions[session_id]
                
                if to_delete:
                    print(f"🧹 Cleaned {len(to_delete)} old sessions")
        except:
            pass

# Start cleanup thread
threading.Thread(target=cleanup_sessions, daemon=True).start()

# ==================== START SERVER ====================
if __name__ == '__main__':
    print("✅ READY!")
    print(f"📡 URL: http://{Config.HOST}:{Config.PORT}")
    print("🌐 Web: http://localhost:5000/static/index.html")
    print("=" * 70)
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=False,
        threaded=True
    )