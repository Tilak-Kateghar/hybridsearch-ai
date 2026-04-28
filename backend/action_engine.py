def generate_actions(context, llm):
    prompt = f"""
    You are an intelligent assistant.

    From the content below, extract:

    1. Key Insights (3 points)
    2. Actionable Steps (2 points)
    3. Important Concepts

    Content:
    {context}

    Format clearly.
    """

    return llm(prompt)