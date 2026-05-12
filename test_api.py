import requests
import json

response = requests.post(
    "http://localhost:8000/chat",
    json={"messages": [{"role": "user", "content": "I am hiring a Senior Java Developer. I need Java 8 Advanced and Verify G+"}]}
)

print(json.dumps(response.json(), indent=2))
