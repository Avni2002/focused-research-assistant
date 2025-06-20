import requests

API_KEY = "f57ef0648cf91221ed48ce2071e57d1a33087498aaab4cb5d2a1c57a72dec671"
query = "latest trends in AI 2025"

params = {
    "q": query,
    "api_key": API_KEY,
    "engine": "google",
    "num": 5
}

response = requests.get("https://serpapi.com/search", params=params)
data = response.json()

results = []

for res in data.get("organic_results", []):
    results.append({
        "title": res.get("title"),
        "snippet": res.get("snippet"),
        "url": res.get("link")
    })

# Print results
for i, result in enumerate(results, 1):
    print(f"{i}. {result['title']}\n{result['snippet']}\n{result['url']}\n")
