from django.shortcuts import render, redirect, get_object_or_404
from .forms import OrderCreateForm
from cart.cart_services import Cart
from .models import OrderProduct, Order
from shop.models import Product
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction


def my_orders(request):
    # Предполагается, что пользователь уже аутентифицирован и его id доступен.
    user_id = request.user.id
    orders = Order.objects.filter(id_user=user_id)  # Получение заказов для пользователя

    # Для каждого заказа получаем соответствующие продукты
    orders_with_products = []
    for order in orders:
        products = order.items.all()  # Используя related_name для доступа к продуктам
        orders_with_products.append((order, products))

    return render(request, 'orders/my_orders.html', {'orders_with_products': orders_with_products})


@login_required
def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.id_user = request.user
                order.save()

                for item in cart.get_cart_items_with_products():  # Используйте метод get_cart_items_with_products
                    product = item['product']
                    quantity = item['quantity']
                    if product.quantity < quantity:
                        # Если товара недостаточно, добавляем сообщение об ошибке
                        messages.error(request, f'Недостаточно товара в наличии')
                        # И перенаправляем пользователя обратно на страницу формы
                        return redirect('orders:order_create')

                    OrderProduct.objects.create(
                        id_order=order,
                        id_product=product,
                        quantity=quantity
                    )

                    # Обновляем количество на складе
                    product.quantity -= quantity
                    product.save()

                # Обновляем общую стоимость заказа и сохраняем заказ
                order.update_total_cost()

                cart.clear_cart()  # Очищаем корзину
                # Перенаправляем пользователя на страницу подтверждения
                return redirect('orders:order_created', order_id=order.id)
        else:
            # Если форма не валидна, мы также добавим сообщение об ошибке
            messages.error(request, 'Ошибка в форме заказа.')
    else:
        form = OrderCreateForm()

    # Если метод не POST или форма не валидна, рендерим страницу с формой заново
    return render(request, 'orders/create.html', {'form': form, 'cart': cart})


def order_created(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/created.html', {'order': order})