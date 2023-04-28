import time
from threading import Thread
from scraper.price_scraper import scrape_prices


def run_scraper():
    while True:
        try:
            scrape_prices()
            # TODO: change time. this is just for a demo
            time.sleep(3600)  # The wait time: 3600 seconds = 1 hour
        except Exception as e:
            print(f"Error: {e}")


def start_scraper_thread():
    scraper_thread = Thread(target=run_scraper)
    scraper_thread.start()
