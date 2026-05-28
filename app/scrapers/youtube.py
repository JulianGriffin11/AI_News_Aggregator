import requests

url = "https://www.youtube.com/channel/UCn8ujwUInbJkBhffxqAPBVQ/videos"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

print("Pinging YouTube to grab raw structural response payload...")
response = requests.get(url, headers=headers, timeout=15)

# Write the raw text output to a local file so we can read it
with open("youtube_dump.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print(f"Handshake Status Code: {response.status_code}")
print("SUCCESS: Raw html dumped into 'youtube_dump.html' inside your project root!")