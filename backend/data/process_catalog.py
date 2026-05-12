import json
import os

def process_catalog():
    input_path = os.path.join(os.path.dirname(__file__), "raw_catalog.json")
    output_path = os.path.join(os.path.dirname(__file__), "catalog.json")

    with open(input_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    KEY_MAP = {
        "Personality & Behavior": "P",
        "Knowledge & Skills": "K",
        "Simulations": "S",
        "Ability & Aptitude": "A",
        "Competencies": "C",
        "Biodata & Situational Judgment": "B",
        "Development & 360": "D",
        "Assessment Exercises": "E"
    }

    processed_data = []
    for item in raw_data:
        keys_list = item.get("keys", [])
        mapped_keys = [KEY_MAP.get(k, k[0]) for k in keys_list]
        test_type_str = ",".join(mapped_keys)
        
        # Map fields to required schema
        processed_item = {
            "name": item.get("name", ""),
            "url": item.get("link", ""),
            "description": item.get("description", ""),
            "duration": item.get("duration", ""),
            "remote_support": item.get("remote", ""),
            "adaptive_support": item.get("adaptive", ""),
            "test_type": test_type_str,
            "keys_full": ", ".join(keys_list), # Keep full string for retrieval
            "category": ", ".join(item.get("job_levels", [])),

            "skills": "", # Assuming skills are inferred from description or title, leaving empty if not present
            "metadata": {
                "entity_id": item.get("entity_id", "")
            }
        }
        processed_data.append(processed_item)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, indent=2)
    print(f"Processed {len(processed_data)} items and saved to {output_path}")

if __name__ == "__main__":
    process_catalog()
