import re

def clean_text(text):
    text = re.sub(r"\s+", " ", text)

    junk_patterns = [
        "Jump to content",
        "Main menu",
        "Search",
        "Donate",
        "Log in",
        "Sign up",
        "Create account",
        "Contents",
        "Toggle",
        "Navigation",
        "Privacy policy",
        "Terms of use"
    ]

    for junk in junk_patterns:
        text = text.replace(junk, "")

    sentences = text.split(".")
    sentences = [s.strip() for s in sentences if len(s.split()) > 5]

    return ". ".join(sentences)


def chunk_text(text, max_words=120, overlap=30):
    text = clean_text(text)

    sentences = re.split(r'(?<=[.!?]) +', text)

    chunks = []
    current_chunk = []

    word_count = 0

    for sentence in sentences:
        words = sentence.split()
        word_count += len(words)

        current_chunk.append(sentence)

        if word_count >= max_words:
            chunk = " ".join(current_chunk)

            if len(chunk) > 80:
                chunks.append(chunk)

            current_chunk = current_chunk[-2:]
            word_count = sum(len(s.split()) for s in current_chunk)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks