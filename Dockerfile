FROM python:3.10-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

WORKDIR /app
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

CMD ["python", "-u", "app.py"]
