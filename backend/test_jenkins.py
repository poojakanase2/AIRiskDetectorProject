import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("JENKINS_URL")
user = os.getenv("JENKINS_USER") or os.getenv("JENKINS_USERNAME")
token = os.getenv("JENKINS_API_TOKEN")

print(f"URL: {url}")
print(f"User: {user}")
print(f"Token length: {len(token) if token else 0}")

try:
    api_url = f"{url}/api/json?tree=jobs[name]"
    response = requests.get(api_url, auth=(user, token), timeout=5)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Jobs found:", [j['name'] for j in response.json().get('jobs', [])])
    else:
        print("Error response:", response.text[:200])
except Exception as e:
    print(f"Connection failed: {e}")
