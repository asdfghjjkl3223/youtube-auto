import os, time, subprocess, threading, random
import gdown
from flask import Flask

# -- CONFIG --
# Yahan apni video files ki alag-alag IDs dalo (comma lagakar)
VIDEO_FILE_IDS = [
    "1TSIlnI-siUSamfqeWLmWgXr6eDxuzZhR",
    "1WVX8TY1ug0rBtvz0aBpndvO710_zIb_8",
    "18MU7ToVUY-59AnUwzUd3dMKKDm7Tc2YX"
]
# Agar abhi ek hi video hai, toh dusri line hata dena, sirf ek ID rakhna.

STREAM_KEY = os.environ.get("STREAM_KEY", "YOUR_STREAM_KEY")
CYCLE_ON_MINUTES = 150 
CYCLE_OFF_MINUTES = 30 

app = Flask(__name__)

@app.route('/')
def keep_alive():
    return "Ekam Devotion Stream is Active!"

def stream_logic():
    while True:
        try:
            # Randomly ek video ID choose karo
            selected_id = random.choice(VIDEO_FILE_IDS)
            print(f"Selected Video ID: {selected_id}")
            
            # Video download karo
            output = 'current_video.mp4'
            url = f'https://drive.google.com/uc?id={selected_id}'
            gdown.download(url, output, quiet=False)
            
            print("Starting Stream Cycle...")
            ffmpeg_cmd = (
                f"ffmpeg -re -stream_loop -1 -i {output} "
                f"-c:v libx264 -preset veryfast -b:v 1500k -maxrate 1500k -bufsize 3000k "
                f"-framerate 10 -g 20 -c:a aac -b:a 128k -ar 44100 -f flv "
                f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
            )
            
            process = subprocess.Popen(ffmpeg_cmd, shell=True)
            time.sleep(CYCLE_ON_MINUTES * 60)
            
            process.terminate()
            
            # Disk space bachane ke liye video delete karo
            if os.path.exists(output):
                os.remove(output)
                
            print(f"Cycle Over. Resting for {CYCLE_OFF_MINUTES} minutes...")
            time.sleep(CYCLE_OFF_MINUTES * 60)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=stream_logic, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
