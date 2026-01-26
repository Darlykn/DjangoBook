from django.db import models
from shop.models import Product
from django.conf import settings
from users.models import CustomUser
from django.core.exceptions import ValidationError


class Order(models.Model):
    """
        Модель Order представляет собой заказ в системе.
        Атрибуты:
        - id_user: Ссылка на покупателя. Если покупатель удалён, поле принимает значение NULL.
        - address: Адрес доставки. Длина ограничена 100 символами.
        - created_date: Дата и время создания заказа. По умолчанию устанавливается текущая дата и время.
        - total_cost: Итоговая стоимость заказа в денежном выражении. Значение по умолчанию — 0.
                      Поле может содержать число до 11 цифр, включая до двух десятичных знаков.
        - status: Статус заказа, может принимать значения: 'wait', 'processing', 'shipped', 'delivered'.
                  По умолчанию установлен в 'wait'.

        Методы:
        - __str__: Возвращает строковое представление заказа.
        - get_total_cost: Вычисляет итоговую стоимость заказа, суммируя стоимости всех товаров.
        - update_total_cost: Обновляет итоговую стоимость заказа в базе данных.
        - clean: Проверяет, что длина адреса не превышает 100 символов.

        Мета-класс:
        - ordering: Сортировка заказов по убыванию даты создания.
        - verbose_name: Читаемое название модели в единственном числе - 'заказ'.
        - verbose_name_plural: Читаемое название модели во множественном числе - 'заказы'.
    """
    id_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, verbose_name="Покупатель",
                                related_name='orders', null=True, blank=True)
    address = models.CharField(max_length=100, verbose_name="Адрес")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    total_cost = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="Общая стоимость", default=0)
    STATUS_CHOICES = (
        ('wait', 'В ожидании'),
        ('processing', 'В сборке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен')
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='wait', verbose_name="Статус")

    class Meta:
        ordering = ('-created_date',)
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return 'Заказ {}'.format(self.id)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    def update_total_cost(self):
        self.total_cost = sum(item.get_cost() for item in self.items.all())
        self.save()

    def clean(self):
        if self.address is not None and len(self.address) > 100:
            raise ValidationError({'address': 'Адрес не должен превышать 100 символов.'})


class OrderProduct(models.Model):
    """
       Модель OrderProduct представляет собой промежуточную модель для управления товарами в заказе.
       Атрибуты:
       - id_order: Ссылка на заказ, к которому относятся товары. При удалении заказа все связанные товары также удаляются.
       - id_product: Ссылка на товар, входящий в состав заказа. При удалении товара все его связи с заказами удаляются.
       - quantity: Количество товара в заказе, по умолчанию установлено в 1.

       Методы:
       - __str__: Возвращает строковое представление объекта.
       - get_cost: Вычисляет стоимость позиции в заказе, умножая цену товара на его количество в заказе.
       """
    id_order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="Заказ")
    id_product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return self.id_product.price * self.quantity
