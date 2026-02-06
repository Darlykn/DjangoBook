from loguru import logger
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .forms import ReviewForm
from .models import *
from orders.models import OrderProduct
from .utils import DataMixin
from cart.forms import CartAddProductForm
from django.shortcuts import render
from django.db.models import Q

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB")


class ShopHome(DataMixin, ListView):
    model = Product
    template_name = 'shop/product/list.html'
    context_object_name = 'products'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get('q')
        context['query'] = q  # Добавляем поисковый запрос в контекст
        if q:  # Проверяем, есть ли поисковый запрос
            products = context['products']
            if products:  # Проверяем, есть ли результаты поиска
                context['title'] = f'Товары по запросу «{q}»'
            else:
                context['title'] = f'По запросу «{q}» ничего не найдено'
        else:
            context['title'] = "Главная"
        return context

    def get_queryset(self):
        queryset = super().get_queryset().select_related('id_category')
        q = self.request.GET.get('q')  # получаем запрос поиска из параметров GET запроса
        if q:
            # Фильтрация на уровне Python для корректной работы с кириллицей
            q_lower = q.lower()
            filtered_ids = [
                product.id for product in queryset
                if q_lower in product.title.lower() or q_lower in product.author.lower()
            ]
            queryset = queryset.filter(id__in=filtered_ids)
        return queryset


class ProductDetailView(DataMixin, DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'shop/product/detail.html'

    def get_object(self, queryset=None):
        product_id = self.kwargs.get('product_id')
        return get_object_or_404(Product, pk=product_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = context['product']
        user = self.request.user

        if user.is_authenticated:
            # Проверяем, есть ли у пользователя заказы, содержащие этот продукт со статусом 'delivered'
            orders_with_product = OrderProduct.objects.filter(
                id_order__id_user=user,
                id_product=product,
                id_order__status='delivered'  # предполагаем, что статус 'delivered' обозначает доставленный заказ
            ).exists()
            context['can_review'] = orders_with_product

            # Проверяем, оставлял ли пользователь уже отзыв на этот продукт
            existing_review = Review.objects.filter(id_product=product, id_user=user).exists()
            context['has_reviewed'] = existing_review
        else:
            context['can_review'] = False
            context['has_reviewed'] = False

        context['category'] = get_object_or_404(Category, id=self.kwargs['category_id'])
        context['review_form'] = ReviewForm()
        context['cart_product_form'] = CartAddProductForm()
        return context

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        review_form = ReviewForm(request.POST)

        if review_form.is_valid() and request.user.is_authenticated:
            # Проверяем, оставлял ли пользователь уже отзыв на этот продукт
            existing_review = Review.objects.filter(id_product=product, id_user=request.user).exists()
            if not existing_review:
                # Создаем новый отзыв, если предыдущий не найден
                Review.objects.create(
                    id_product=product,
                    id_user=request.user,
                    rating=review_form.cleaned_data['rating'],
                    text=review_form.cleaned_data['text']
                )
            return redirect(product.get_absolute_url())

        context = self.get_context_data()
        context['review_form'] = review_form
        return self.render_to_response(context)


class ShopCategory(DataMixin, ListView):
    model = Product
    template_name = 'shop/product/list.html'
    context_object_name = 'products'
    allow_empty = True  # разрешаем отображение пустых категорий

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs.get('category_id'):
            category = get_object_or_404(Category, pk=self.kwargs['category_id'])
            context['category'] = category  # Добавляем категорию в контекст
            context['title'] = 'Категория - ' + category.title.upper()
        else:
            context['title'] = 'Новинки'
        return context

    def get_queryset(self):
        return Product.objects.filter(id_category_id=self.kwargs['category_id'])


def about(request):
    return render(request, 'shop/product/about.html')

