def is_valid_chunk(text: str):
    text = text.strip()

    if len(text.split()) < 12:
        return False

    junk_patterns = [
        "jump to content",
        "main menu",
        "search",
        "donate",
        "log in",
        "create account",
        "contents hide",
        "toggle"
    ]

    lower = text.lower()

    for junk in junk_patterns:
        if junk in lower:
            return False

    return True