import requests
import json

url = "http://localhost:8000/api/analyze-log"
data = {
    "log_text": "npm ERR! 404 'expresss@latest' is not in the npm registry"
}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
