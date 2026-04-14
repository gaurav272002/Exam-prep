import requests

response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    },
    json={
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": "Extract syllabus structure from this text"
            }
        ]
    }
)

print(response.json())