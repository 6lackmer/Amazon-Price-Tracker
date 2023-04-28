import requests
from bs4 import BeautifulSoup
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.conf import settings

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
application = get_wsgi_application()

from my_app.utils import send_test_email

send_test_email()

def send_test_email():
    subject = 'Hello from Zoho Mail'
    message = 'This is a test email sent using Zoho Mail as the email provider.'
    from_email = 'your_username@your_domain.com'
    recipient_list = ['recipient@example.com']

    send_mail(subject, message, from_email, recipient_list)
send_test_email()

# def get_amazon_price(url):
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
#     }
#     response = requests.get(url, headers=headers)
#
#     if response.status_code != 200:
#         return None
#
#     soup = BeautifulSoup(response.text, 'lxml')
#     price = soup.select_one('#price_inside_buybox, #priceblock_ourprice')
#
#     if price is None:
#         return None
#
#     return float(price.text.strip().replace('$', ''))
#
#
# class Command(BaseCommand):
#     help = 'Checks the prices of tracked Amazon items and sends an email if the price falls below the target price'
#
#     def handle(self, *args, **options):
#         tracked_items = TrackedItem.objects.all()
#
#         for item in tracked_items:
#             current_price = get_amazon_price(item.product_link)
#
#             if current_price is not None and current_price <= item.target_price:
#                 user = User.objects.get(id=item.user.id)
#
#                 send_mail(
#                     subject=f'Amazon Price Tracker: Price Alert for {item.product_title}',
#                     message=f'The price for {item.product_title} has dropped to ${current_price}. Visit the product page: {item.product_link}',
#                     from_email=settings.EMAIL_HOST_USER,
#                     recipient_list=[user.email],
#                     fail_silently=False,
#                 )
#
#                 self.stdout.write(self.style.SUCCESS(f'Successfully sent email to {user.email}'))
#             else:
#                 self.stdout.write(self.style.WARNING(f'No price change for {item.product_title}'))
