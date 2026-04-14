import requests

response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": "Bearer ",
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