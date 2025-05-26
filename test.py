import requests

API_KEY = "AIzaSyBC2UBYGZe743ctVuzbHrqsNULxHAFrJ6A"

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=GEMINI_API_KEY"
headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": API_KEY
}

body = {
    "contents": [
        {"parts": [{"text": "Say hello in JSON format"}]}
    ]
}

response = requests.post(url, headers=headers, json=body)

print("Status Code:", response.status_code)
print("Response:")
print(response.text)
