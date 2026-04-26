import os, time, subprocess, threading, random
import gdown
from flask import Flask

# -- CONFIG --
# Screenshot mein jo '/folders/' ke baad wali ID thi, wo yahan dalo
DRIVE_FOLDER_ID = "1-kkazE2zB4grKqtSNFdgaTLTSAVtUxDK" 
STREAM_KEY = os.environ.get("STREAM_KEY", "YOUR_STREAM_KEY")
CYCLE_ON_MINUTES = 150 
CYCLE_OFF_MINUTES = 30 

app = Flask(__name__)

@app.route('/')
def keep_alive():
    return "Bhajan Folder Stream is Active!"

def get_video_list():
    print("Scanning Google Drive folder...")
    # Ise folder scan karne ke liye use karenge
    url = f'https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}'
    # gdown folder scan karke saari file IDs nikal sakta hai
    files = gdown.list_objects(url, fuzzy=True)
    # Sirf mp4 files filter karo
    video_files = [f for f in files if f.name.endswith('.mp4')]
    return video_files

def stream_logic():
    while True:
        try:
            videos = get_video_list()
            if not videos:
                print("Folder mein koi video nahi mili! 5 min wait kar raha hu...")
                time.sleep(300)
                continue
            
            # Randomly ek video choose karo
            selected_video = random.choice(videos)
            print(f"Selected Video: {selected_video.name}")
            
            # Video download karo
            output = 'current_video.mp4'
            gdown.download(id=selected_video.id, output=output, quiet=False)
            
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
