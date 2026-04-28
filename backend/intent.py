def detect_intent(query):
    query = query.lower()

    if "summary" in query:
        return "summary"
    elif "compare" in query:
        return "compare"
    elif "why" in query or "how" in query:
        return "explanation"
    else:
        return "qa"