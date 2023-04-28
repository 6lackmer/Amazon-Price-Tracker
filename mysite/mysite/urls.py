"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from scraper import views as scraper_views
from users import views as user_views
from django.contrib.auth import views as authentication_views
from scraper import run_scraper

run_scraper.start_scraper_thread()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', scraper_views.index, name='index'),
    path('update_price/', scraper_views.update_price, name='update_price'),
    path('unsubscribe/', scraper_views.unsubscribe, name='unsubscribe'),
    path('my_products/', scraper_views.my_products, name='my_products'),
    path('add_tracked_item/', scraper_views.add_tracked_item, name='add_tracked_item'),
    path('search/', scraper_views.scrape, name='scrape'),
    path('register/', user_views.register, name='register'),
    path('login/', authentication_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', authentication_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('external_redirect/', scraper_views.redirect_view, name='redirect_view'),  # view to redirect to amazon
]
