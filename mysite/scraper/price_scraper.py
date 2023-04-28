from django.core.mail import send_mail
from django.conf import settings
from scraper.models import TrackedItem
from bs4 import BeautifulSoup
from scraper.views import get_chrome_options
from selenium import webdriver
from decimal import Decimal

def scrape_prices():
    browser = webdriver.Chrome(options=get_chrome_options())
    tracked_items = TrackedItem.objects.all()

    for item in tracked_items:
        try:
            url = item.product_link
            browser.get(url)
            soup = BeautifulSoup(browser.page_source, 'html.parser')

            price_span = soup.select_one('span.a-price-whole')
            price_dollar = price_span.get_text().replace('.', '')

            price_span = soup.select_one('span.a-price-fraction')
            price_cents = price_span.get_text().replace('.', '')
            current_price = Decimal(price_dollar) + (Decimal(price_cents) / 100)

            if current_price != item.product_price:
                print(f'Price change for {item.product_title} from {item.product_price} to {current_price}')
                item.product_price = current_price
                item.save()

            if current_price <= item.target_price:
                subject = f'Price Alert: {item.product_title}'
                message = f'The price for {item.product_title} has dropped to ${current_price}.\n\n' \
                          f'You can check it out here: {item.product_link}'
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [item.user.email]

                send_mail(subject, message, from_email, recipient_list)
                print(f'Sent price alert for {item.product_title} to {item.user.email}')
        except Exception as err:
            print(f'Error processing {item.product_title}: {err}')
