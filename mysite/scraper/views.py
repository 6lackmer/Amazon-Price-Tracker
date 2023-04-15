from django.shortcuts import render, redirect
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from decimal import Decimal

def get_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    return chrome_options

def redirect_view(request):
    link = "https://amazon.com/" + request.GET.get('link')
    return redirect(link)

def scrape(request):
    browser = webdriver.Chrome(options=get_chrome_options())

    search_query = request.GET.get('search', '')
    url = 'https://www.amazon.com/s?k=' + search_query

    # If the user is loading the search page without a query
    if url == 'https://www.amazon.com/s?k=':
        return render(request, 'scraper/result.html', {'combined_data': [], 'message': "Please search for an item..."})

    browser.get(url)

    soup = BeautifulSoup(browser.page_source, 'html.parser')
    search_results = soup.select('.s-result-item')

    product_data = {}

    for result in search_results:
        try:
            # Extract image URL, product title, price, and product link
            img = result.select_one('img.s-image')
            title = result.select_one('span.a-size-base-plus.a-color-base.a-text-normal')
            price_span = result.select_one('span.a-price-whole')
            price_fraction = result.select_one('span.a-price-fraction')
            link = result.select_one('a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')

            if img and title and price_span and price_fraction and link:
                img_url = img['src']
                product_title = title.text

                price = Decimal(price_span.get_text().replace(',', '')) + Decimal(price_fraction.get_text()) / 100
                product_price = "{:.2f}".format(price)

                product_link = link['href']

                # Prevents duplicates
                if product_title not in product_data:
                    product_data[product_title] = (img_url, product_price, product_link)

        except Exception as e:
            print(f"Error processing search result: {e}")

    # used to find the last value in the pagination, so we can get the number of pages.
    pagination_items = soup.select('.s-pagination-item')

    num_pages = 0
    for item in pagination_items:
        if item.text.isdigit():
            current_page_number = int(item.text)
            if current_page_number > num_pages:
                num_pages = current_page_number

    browser.quit()

    # Combine the data
    combined_data = [(img_url, product_title, product_price, link) for product_title, (img_url, product_price, link) in product_data.items()]
    return render(request, 'scraper/result.html', {'combined_data': combined_data, 'current_page': 7, 'num_pages': num_pages})
