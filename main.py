import json
import time
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

BASE_URL = "https://metroidconstruction.com"
URL = "https://metroidconstruction.com/hacks.php?sort=&dir=&filters%5B%5D=SM&filters%5B%5D=Unknown&filters%5B%5D=Boss+Rush&filters%5B%5D=Exploration&filters%5B%5D=Challenge&filters%5B%5D=Spoof&filters%5B%5D=Speedrun%2FRace&filters%5B%5D=Incomplete&filters%5B%5D=Quick+Play&filters%5B%5D=Improvement&filters%5B%5D=Vanilla%2B&search=&num_per_page=500"

HACK_URLS = {}
HACK_INFO = {}
GET_HACK_URLS = False
GET_HACK_INFO = False
GET_HACK_FILE = True

with open("info.json") as info_json_file:
    HACK_URLS = json.load(info_json_file)

with open("hack_details.json") as hack_details_file:
    HACK_INFO = json.load(hack_details_file)

if GET_HACK_URLS:
    payload = requests.get(URL)
    soup = BeautifulSoup(payload.content, "html.parser")
    table_rows = soup.find("tbody").find_all("tr")
    for tr in table_rows:
        cell = tr.find_all("td")[0]
        url = cell.find("a", href=True)
        name = url.text
        HACK_URLS[urljoin(BASE_URL, url["href"])] = name
    with open("info.json", "w") as info_json_file:
        json.dump(HACK_URLS, info_json_file, indent=4)

def parse_description(cell, hack_info):
    text = cell.text.strip()
    if "Release date" in text:
        hack_info["release_date"] = text.split(":")[1].strip()
    elif "Difficulty" in text:
        hack_info["difficulty"] = text.split(":")[1].strip().replace("[?]","")
    elif "Genre" in text:
        hack_info["genre"] = text.split(":")[1].strip().replace("[?]","")
    elif "Average runtime" in text:
        hack_info["average_runtime"] = text.split(":")[1].strip()
    elif "Author" in text:
        hack_info["author"] = text.split(":")[1].strip()
    elif "Average collection" in text:
        hack_info["average_collection"] = text.split(":")[1].strip()
    elif "Awards" in text:
        hack_info["awards"] = text.split("Awards:")[1].strip()
    elif "Rating" in text:
        if "Pending" in text:
            hack_info["rating"] = "Pending"
        else:
            span = cell.find("span").find("span")
            rating = span.attrs.get("title").strip().split(":")[1].split("chozo orbs")[0]
            hack_info["rating"] = rating.strip()
    elif "Download" in text:
        href = cell.find("a", href=True)
        hack_info["download_url"] = href.text

if GET_HACK_FILE:
    for url, name in HACK_URLS.items():
        if name not in HACK_INFO:
            print(f"Starting: {name}")
            hack_info = {}
            time.sleep(1)
            payload = requests.get(url)
            soup = BeautifulSoup(payload.content, "html.parser")
            table_rows = soup.find_all("table")[1].find("tr", recursive=False).find_all("tr")
            for tr in table_rows:
                cells = tr.find_all("td", recursive=False)
                for cell in cells:
                    parse_description(cell, hack_info)
            HACK_INFO[name] = hack_info
        else:
            print(f"Already loaded: {name}")

    with open("hack_details.json", "w") as hack_info_file:
        json.dump(HACK_INFO, hack_info_file, indent=4)






