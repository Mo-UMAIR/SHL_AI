import json
import urllib.request
import os

URL = "https://tcp-us-prod-rnd.shl.com/voiceRater/shl-ai-hiring/shl_product_catalog.json"
OUTPUT_FILE = "catalog.json"

def fetch_and_process_catalog():
    print(f"Fetching catalog from {URL}...")
    try:
        req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            text_data = response.read().decode('utf-8')
            data = json.loads(text_data, strict=False)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    processed_assessments = []
    
    # Analyze the structure (assuming it's a list or a dict with a list of products)
    items = data if isinstance(data, list) else data.get('products', [])
    if not items and isinstance(data, dict):
        # Maybe the keys are categories? Let's just flatten if needed.
        # But looking at SHL JSON, it's often a list of dictionaries.
        items = data

    print(f"Total items fetched: {len(items)}")

    count = 0
    for item in items:
        # Assuming we need to filter by some type field
        # The exact structure is unknown without viewing it, but we can make educated guesses 
        # based on standard SHL catalog structures or the problem statement.
        # Let's save the raw data first so we can analyze its structure.
        pass

    with open("raw_catalog.json", "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)
    print("Saved raw catalog to raw_catalog.json for inspection.")

if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    
    # Change to script directory so files are saved here
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    fetch_and_process_catalog()
