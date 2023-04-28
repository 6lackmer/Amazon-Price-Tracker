from django.shortcuts import render, redirect
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from .models import TrackedItem
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

def index(request):
    return render(request, 'scraper/index.html')


@login_required
def unsubscribe(request):
    if request.method == 'POST':
        product_id = request.POST.get('id')

        tracked_item = TrackedItem.objects.get(id=product_id)
        tracked_item.delete()
        messages.success(request, "Unsubscribed from item")
        return HttpResponseRedirect(reverse('my_products'))

@login_required
def update_price(request):
    if request.method == 'POST':
        product_id = request.POST.get('id')
        new_target_price = Decimal(request.POST.get('target_price'))

        tracked_item = TrackedItem.objects.get(id=product_id)

        if new_target_price >= tracked_item.product_price:
            messages.warning(request, "Tracking price must be less than the price")
            return HttpResponseRedirect(reverse('my_products'))
        elif new_target_price <= 0:
            messages.warning(request, "Tracking price must be larger than $0.00")
            return HttpResponseRedirect(reverse('my_products'))
        else:
            messages.success(request, "Tracking price Updated")
            tracked_item.target_price = new_target_price
            tracked_item.save()
            return HttpResponseRedirect(reverse('my_products'))



@login_required
def my_products(request):
    user = request.user
    tracked_items = TrackedItem.objects.filter(user=user)

    return render(request, 'scraper/my_products.html', {'tracked_items': tracked_items})

# Get the options for chrome. Beautiful Soup wouldn't scrape, so we are using a chrome driver and selenium.
def get_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    return chrome_options


def redirect_view(request):
    link = "https://amazon.com/" + request.GET.get('link')
    return redirect(link)


@login_required
def add_tracked_item(request):
    if request.method == 'POST':
        # Save the tracked product
        user = request.user
        product_title = request.POST.get('product_title')
        img_url = request.POST.get('img_url')
        product_link = request.POST.get('product_link')
        product_link = "https://amazon.com/" + product_link

        product_price = request.POST.get('product_price')
        target_price = request.POST.get('target_price')

        # Check if the product already exists for the user
        duplicate_item = TrackedItem.objects.filter(
            user=user, product_link=product_link).exists()
        if duplicate_item:
            # Show a message to the user if the product already exists
            messages.warning(request, "This product is already being tracked.")
        else:
            if Decimal(target_price) < Decimal(product_price):
                # Save the tracked product if the target price is lower than the current product price
                messages.success(request, 'Product Tracked')
                tracked_item = TrackedItem(
                    user=user,
                    product_title=product_title,
                    img_url=img_url,
                    product_link= product_link,
                    product_price=product_price,
                    target_price=target_price
                )
                tracked_item.save()
            else:
                messages.warning(request, "Target price should be lower than the current price.")

            return HttpResponseRedirect(reverse('my_products'))

        return HttpResponseRedirect(reverse('my_products'))


@login_required
def scrape(request):
    browser = webdriver.Chrome(options=get_chrome_options())

    search_query = request.GET.get('search', '')

    print(f"search query: {search_query}")

    # create the url for amazon, default is the first page
    current_page = int(request.GET.get('current_page', 1))
    url = f'https://www.amazon.com/s?k={search_query}&page={current_page}'

    # if no search query was scraped
    if url == 'https://www.amazon.com/s?k=&page=1':
        return render(request, 'scraper/result.html', {'combined_data': [], 'message': "Please search for an item..."})

    # get the page and parse it
    browser.get(url)

    soup = BeautifulSoup(browser.page_source, 'html.parser')
    search_results = soup.select('.s-result-item')

    product_data = {}
    for result in search_results:
        try:
            # Extract image URLs, product titles, product prices, and product links from the page
            img = result.select_one('img.s-image')
            title = result.select_one(
                'span.a-size-base-plus.a-color-base.a-text-normal')
            price_span = result.select_one('span.a-price-whole')
            price_fraction = result.select_one('span.a-price-fraction')
            link = result.select_one(
                'a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')

            if img and title and price_span and price_fraction and link:
                # get the images
                img_url = img['src']
                product_title = title.text

                # get the price and format it
                price = Decimal(price_span.get_text().replace(
                    ',', '')) + Decimal(price_fraction.get_text()) / 100
                product_price = "{:.2f}".format(price)

                # get the product links
                product_link = link['href']

                # Prevents duplicates
                if product_title not in product_data:
                    product_data[product_title] = (
                        img_url, product_price, product_link)

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
    combined_data = [(img_url, product_title, product_price, link) for product_title, (img_url, product_price, link) in
                     product_data.items()]
    return render(request, 'scraper/result.html',
                  {'combined_data': combined_data, 'current_page': current_page, 'num_pages': num_pages,
                   'search_query': search_query})
