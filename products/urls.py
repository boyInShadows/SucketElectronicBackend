from django.urls import path
from .views import latest_products

urlpatterns = [
    path('latest/', latest_products, name='latest-products'),
] 