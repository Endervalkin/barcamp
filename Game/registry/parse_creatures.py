import os
import csv
import json
# Define paths for the CSV and JSON files
import sys 

script_dir = os.path.dirname(__file__)
csv_path = os.path.join(script_dir, "..", "data", "units", "creatures.csv")
json_path = os.path.join(script_dir, "..", "data", "units", "creatures_data.json")

# Run the parser
def parse_creature_csv(csv_path, json_path):
    """
    Parses a CSV file containing creature data and writes the results to a JSON file.

    Args:
        csv_path (str): Path to the input CSV file.
        json_path (str): Path to the output JSON file.

    Returns:
        dict: A dictionary mapping creature names to their data.
    """
    creatures = {}
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Normalize header field names to avoid BOM issues
        
        reader.fieldnames = [name.strip().lstrip("\ufeff") for name in reader.fieldnames]
        print("CSV headers:", reader.fieldnames)
        for row in reader:
            name = row.get("creature_name", "").strip()
            try:
                level = int(row["creature_level"])
            except (ValueError, KeyError):
                print(f"Skipping row with invalid or missing creature_level: {row}")
                continue
            creatures[name] = { "creature_level": level }

    if json_path:
        with open(json_path, "w", encoding="utf-8") as out:
            json.dump(creatures, out, indent=2)
    if json_path:
        print(f"Successfully parsed and saved creatures from {csv_path} to {json_path}")
    else:
        print(f"Successfully parsed creatures from {csv_path} (no JSON output file specified)")
    return creatures
if __name__ == "__main__":
    parse_creature_csv(csv_path, json_path)