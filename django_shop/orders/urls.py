from django.urls import path
from .views import order_create, order_created, my_orders

app_name = 'orders'

urlpatterns = [
    path('create/', order_create, name='order_create'),
    path('created/<int:order_id>/', order_created, name='order_created'),
    path('my-orders/', my_orders, name='my-orders'),
]
