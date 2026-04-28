from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(url: str):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return None


from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(url: str):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return None


def get_transcript(url):
    video_id = extract_video_id(url)

    if not video_id:
        return []

    print("VIDEO ID:", video_id)

    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        for lang in ['en', 'hi']:
            try:
                transcript = transcript_list.find_transcript([lang]).fetch()
                break
            except:
                continue
        else:
            transcript = transcript_list.find_generated_transcript(['en']).fetch()

        return [
            {
                "text": t["text"].strip(),
                "timestamp": t["start"]
            }
            for t in transcript
            if len(t["text"].strip()) > 10
        ]

    except Exception as e:
        print("Transcript error:", str(e))
        return []