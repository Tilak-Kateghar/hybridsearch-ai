import requests
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def groq_llama_8b(prompt):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0
        }

        res = requests.post(url, json=data, headers=headers, timeout=10)
        return res.json()["choices"][0]["message"]["content"]

    except Exception as e:
        print("Groq error:", e)
        return None


def gemini_flash(prompt):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

        data = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        res = requests.post(url, json=data, timeout=10)
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        print("Gemini error:", e)
        return None


def ask_llm_api(prompt, mode="fast"):
    if mode == "fast":
        res = groq_llama_8b(prompt)
        if res:
            return res

    # fallback
    return gemini_flash(prompt) or "LLM unavailable"