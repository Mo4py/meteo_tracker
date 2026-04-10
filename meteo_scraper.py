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

    for url in URLS:
        try:
            print(f"Scraping {url}...")
            response = requests.get(url, timeout=15)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text()

            # 1. Extract Station Name (text after "Wetterstation")
            # This looks for "Wetterstation" and stops at the next newline or "Werte am"
            name_match = re.search(r"Wetterstation\s+(.*?)(?:\r?\n|Werte am|$)", page_text)
            station_name = name_match.group(1).strip() if name_match else "Unknown Station"

            # 2. Extract Timestamp from site
            time_match = re.search(r"Werte am\s*([\d-]+\s[\d:]+)", page_text)
            site_time = time_match.group(1) if time_match else "N/A"

            # 3. Extract Temperature
            temp_match = re.search(r"Lufttemperatur.*?([\d.]+)", page_text, re.DOTALL)
            temp_value = temp_match.group(1) if temp_match else "N/A"

            if site_time != "N/A" and temp_value != "N/A":
                results.append([station_name, site_time, temp_value])
                print(f"  Captured: {station_name} | {temp_value}°C")
            else:
                print(f"  Warning: Missing data for {url}")

        except Exception as e:
            print(f"  Error scraping {url}: {e}")

    # Save all results to CSV
    if results:
        file_exists = os.path.isfile(FILE_NAME)
        with open(FILE_NAME, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Station", "Site_Timestamp", "Temperature"])
            writer.writerows(results)

if __name__ == "__main__":
    scrape_onoca()