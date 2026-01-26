from django.urls import path
from .views import ShopHome, ShopCategory, ProductDetailView, about

app_name = 'shop'

urlpatterns = [
    path('', ShopHome.as_view(), name='product_list'),
    path('category/<int:category_id>/', ShopCategory.as_view(), name='product_list_by_category'),
    path('category/<int:category_id>/product/<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    path('about/', about, name='about'),
]
