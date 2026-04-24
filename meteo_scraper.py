import requests
from bs4 import BeautifulSoup
import os
import re
import csv


URLS = [
    "https://w1.onoca.de/",
    "https://w3.onoca.de/",
    "https://w6.onoca.de/",
    "https://w9.onoca.de/"
]
FILE_NAME = "meteo_data.csv"

def scrape_onoca():
    results = []
    
    # 1. Load existing data to check for duplicates
    existing_records = set()
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if len(row) >= 2:
                    existing_records.add((row[0], row[1]))
                    
    for url in URLS:
        try:
            print(f"Scraping {url}...")
            response = requests.get(url, timeout=15)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text()

            # 2. Extract Station Name
            name_match = re.search(r"Wetterstation\s+(.*?)(?:\r?\n|Werte am|$)", page_text)
            station_name = name_match.group(1).strip() if name_match else "Unknown Station"

            # 3. Extract Timestamp
            time_match = re.search(r"Werte am\s*([\d-]+\s[\d:]+)", page_text)
            site_time = time_match.group(1) if time_match else "N/A"

            # 4. Extract Temperature
            temp_match = re.search(r"Lufttemperatur.*?([\d.]+)", page_text, re.DOTALL)
            temp_value = temp_match.group(1) if temp_match else "N/A"

            if site_time != "N/A" and temp_value != "N/A":
                # Only add if it's not already in the CSV
                if (station_name, site_time) not in existing_records:
                    results.append([station_name, site_time, temp_value])
                    print(f"  Captured: {station_name} | {temp_value}°C")
                else:
                    print(f"  Skipped: {station_name} (Data already exists for {site_time})")
            else:
                print(f"  Warning: Missing data for {url}")

        except Exception as e:
            print(f"  Error scraping {url}: {e}")

    # 5. Save all new results to CSV
    if results:
        file_exists = os.path.isfile(FILE_NAME)
        with open(FILE_NAME, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Station", "Site_Timestamp", "Temperature"])
            writer.writerows(results)

if __name__ == "__main__":
    scrape_onoca()
