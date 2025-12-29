import re
import os
import sys
import asyncio
import edge_tts
import subprocess
import time

# Configuration
VOICE = "zh-CN-XiaoxiaoNeural"
RATE = "+10%"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "temp_speech.mp3")
PID_FILE = os.path.join(BASE_DIR, "player.pid")
VBS_PLAYER = os.path.join(BASE_DIR, "silent_player.vbs")

def clean_markdown(text):
    """Clean markdown for TTS."""
    text = re.sub(r'^---\n.*?---\n', '', text, flags=re.DOTALL)
    text = re.sub(r'```.*?```', " [此处包含代码，建议查看屏幕] ", text, flags=re.DOTALL)
    text = re.sub(r'`([^`]*)`', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    text = re.sub(r'^\s*-\s*\[x\]\s*', '已完成：', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*-\s*\[\s\]\s*', '待完成：', text, flags=re.MULTILINE)
    return text

async def generate_audio(text):
    """Generate MP3 using Edge-TTS."""
    # Ensure BASE_DIR exists
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
        
    print(f"☁️ Generating High-Quality Voice...")
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
    await communicate.save(OUTPUT_FILE)
    print(f"✅ Audio generated: {os.path.getsize(OUTPUT_FILE)} bytes")

def create_vbs_player():
    """Create a silent VBScript player file."""
    vbs_content = '''
Set Player = CreateObject("WMPlayer.OCX")
Player.URL = WScript.Arguments(0)
Player.Controls.Play
' Wait for it to start playing
Do While Player.playState = 0 or Player.playState = 9 or Player.playState = 10
    WScript.Sleep 100
Loop
' Keep running while playing
Do While Player.playState <> 1
    WScript.Sleep 500
Loop
'''
    with open(VBS_PLAYER, 'w') as f:
        f.write(vbs_content)

def stop_playback():
    """Kill the background player process."""
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            if os.name == 'nt':
                # Kill cscript.exe by its PID
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], capture_output=True)
            else:
                os.kill(pid, 15)
            print("⏹️ Stopped previous playback.")
        except:
            pass
        finally:
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
    
    # Also kill any wandering cscript or wmplayer? Too aggressive. 
    # Just killing by PID is enough.

def play_audio_background():
    """Play MP3 in background using VBScript (Windows)."""
    stop_playback()
    create_vbs_player()

    if not os.path.exists(OUTPUT_FILE):
        print("❌ Error: Audio file missing.")
        return

    print("▶️ Playing in background (Silent)...")
    
    if os.name == 'nt':
        try:
            # We use cscript to run the VBScript silently
            cmd = ['cscript', '//Nologo', VBS_PLAYER, OUTPUT_FILE]
            process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
            
            with open(PID_FILE, 'w') as f:
                f.write(str(process.pid))
        except Exception as e:
            print(f"❌ Playback failed: {e}")
    else:
        # Non-Windows fallback
        player = 'afplay' if sys.platform == 'darwin' else 'mpg123'
        process = subprocess.Popen([player, OUTPUT_FILE], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with open(PID_FILE, 'w') as f:
            f.write(str(process.pid))

def read_file(file_path):
    """Main entry point for reading."""
    if file_path == "stop":
        stop_playback()
        return

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    cleaned = clean_markdown(content)
    try:
        # Check if already in an event loop (e.g. running in some environments)
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # This happens in some REPLs or GUI frameworks
                import threading
                def run_async():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    new_loop.run_until_complete(generate_audio(cleaned))
                    play_audio_background()
                threading.Thread(target=run_async).start()
                return
        except:
            pass

        asyncio.run(generate_audio(cleaned))
        play_audio_background()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        read_file(sys.argv[1])
