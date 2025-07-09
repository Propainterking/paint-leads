from config import LOCATIONS, KEYWORDS
from utils import write_csv, sync_to_google_sheets, send_email
from platforms import yelp_scraper, craigslist_scraper, yellowpages_scraper
import datetime
import os

def run_all_scrapers():
    all_leads = []
    os.makedirs("output", exist_ok=True)
    log_path = "output/log.txt"
    with open(log_path, "w") as log:
        log.write(f"Lead scrape run: {datetime.datetime.now()}\n")

        for location in LOCATIONS:
            for keyword in KEYWORDS:
                for scraper, name in [
                    (yelp_scraper.scrape, "Yelp"),
                    (craigslist_scraper.scrape, "Craigslist"),
                    (yellowpages_scraper.scrape, "YellowPages")
                ]:
                    try:
                        leads = scraper(keyword, location)
                        log.write(f"{name} for {location} + {keyword}: {len(leads)} leads\n")
                        all_leads += leads
                    except Exception as e:
                        log.write(f"{name} failed: {str(e)}\n")

    # Remove duplicates
    seen = set()
    clean_leads = []
    for lead in all_leads:
        key = (lead[1], lead[2])  # Name + Address
        if key not in seen:
            seen.add(key)
            clean_leads.append(lead)

    write_csv(clean_leads)
    sync_to_google_sheets(clean_leads)
    send_email(clean_leads)

if __name__ == "__main__":
    run_all_scrapers()
