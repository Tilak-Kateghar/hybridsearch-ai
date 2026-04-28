import whisper
import yt_dlp
import os
import uuid

model = whisper.load_model("tiny")


def download_audio(url):
    filename = f"audio_{uuid.uuid4().hex}.mp3"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': filename,
        'quiet': True,
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return filename
    except Exception as e:
        print("yt-dlp error:", str(e))
        return None


def merge_segments(segments, window=4):
    merged = []

    for i in range(0, len(segments), window):
        chunk = segments[i:i+window]

        text = " ".join([s["text"].strip() for s in chunk])

        if len(text.split()) > 15:
            merged.append({
                "text": text,
                "timestamp": chunk[0]["start"]
            })

    return merged


def whisper_transcript(url):
    try:
        file_path = download_audio(url)

        if not file_path or not os.path.exists(file_path):
            return []

        result = model.transcribe(file_path)

        segments = result["segments"]

        chunks = merge_segments(segments)

        os.remove(file_path)

        return chunks[:20]

    except Exception as e:
        print("Whisper error:", str(e))
        return []