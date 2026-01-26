from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from users.models import CustomUser
from django.conf import settings


class Category(models.Model):
    """
        Модель Category представляет собой категорию товаров в системе.
        Атрибуты:
        - title: Название категории. Должно быть уникальным и ограничено 30 символами.

        Методы:
        - __str__: Возвращает название категории.
        - get_absolute_url: Возвращает URL для отображения списка товаров данной категории.
        - clean: Проверяет, что длина названия категории не превышает 30 символов.

        Мета-класс:
        - ordering: Сортировка категорий по названию.
        - verbose_name: Читаемое название модели в единственном числе - 'категория'.
        - verbose_name_plural: Читаемое название модели во множественном числе - 'категории'.
    """

    title = models.CharField(max_length=30, unique=True, verbose_name='название категории')

    class Meta:
        """Используем для задания параметров в админке"""
        ordering = ('title',)  # сортировка применяется и в отображении в админке и в шаблонах
        verbose_name = 'категории'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.id])

    def clean(self):
        if self.title is not None and len(self.title) > 30:
            raise ValidationError({'title': 'Название категории не должно превышать 30 символов'})


class Product(models.Model):
    """
        Модель Product представляет собой товар в системе.
        Атрибуты:
        - title: Название товара. Ограничено 100 символами.
        - author: Автор книги. Ограничено 100 символами.
        - description: Описание товара, может быть пустым. Ограничено 1000 символами.
        - price: Цена товара. Максимальное количество цифр 9, включая два десятичных знака.
        - quantity: Количество товара на складе. По умолчанию установлено в 0.
        - image: Изображение товара.
        - id_category: Ссылка на категорию, к которой относится товар.

        Методы:
        - __str__: Возвращает название товара.
        - get_absolute_url: Возвращает URL для детального просмотра товара.
        - get_average_review_score: Вычисляет средний рейтинг товара на основе отзывов.
        - clean: Проверяет валидность данных: длины строк и положительность цены.

        Мета-класс:
        - ordering: Сортировка товаров по названию.
        - verbose_name: Читаемое название модели в единственном числе - 'товар'.
        - verbose_name_plural: Читаемое название модели во множественном числе - 'товары'.
    """
    title = models.CharField(max_length=100, verbose_name='Название')
    author = models.CharField(max_length=100, verbose_name='Автор')
    description = models.TextField(max_length=1000, verbose_name='Описание', null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество')
    image = models.ImageField(verbose_name='Изображение')
    id_category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'товар'  # отображение названия в админке
        verbose_name_plural = 'товары'  # отображение названия в админке
        ordering = ('title',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id_category.id, self.id])

    def get_average_review_score(self):
        """Вычисляем средний рейтинг товара. self.reviews возвращает все связанные объекты Review для данного объекта Product"""
        average_score = 0.0
        if self.reviews.count() > 0:
            total_score = sum([review.rating for review in self.reviews.all()])
            average_score = total_score / self.reviews.count()
        return round(average_score, 1)

    def clean(self):
        if self.title is not None and len(self.title) > 100:
            raise ValidationError({'title': 'Название товара не должно превышать 100 символов.'})
        if self.author is not None and len(self.author) > 100:
            raise ValidationError({'author': 'Имя автора не должно превышать 100 символов.'})
        if self.description is not None and len(self.description) > 1000:
            raise ValidationError({'description': 'Описание не должно превышать 1000 символов.'})
        if self.price is not None and self.price < 0:
            raise ValidationError({'price': 'Цена должна быть положительной.'})


class Review(models.Model):
    """
        Модель Review представляет собой отзыв пользователя на товар.
        Атрибуты:
        - id_product: Ссылка на товар, к которому оставлен отзыв. Удаление товара приведет к удалению всех его отзывов.
        - id_user: Ссылка на пользователя, оставившего отзыв. Если пользователь удаляется, отзыв остается,
                   но без привязки к пользователю.
        - rating: Рейтинг товара, выставленный пользователем. Допустимые значения от 1 до 5.
        - text: Текст отзыва, может быть пустым. Ограничен 200 символами.
        - created_date: Дата и время создания отзыва, устанавливается автоматически при создании.

        Методы:
        - clean: Проверяет, что текст отзыва не превышает 200 символов.
        - save: Перед сохранением отзыва в базу данных проверяет корректность рейтинга.

        Мета-класс:
        - ordering: Сортировка отзывов по убыванию даты создания.
    """
    id_product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE, verbose_name='Продукт')
    id_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='reviews', verbose_name='Автор')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='Рейтинг')
    text = models.TextField(null=True, max_length=200, blank=True, verbose_name='Текст')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        ordering = ('-created_date', )

    def clean(self):
        if self.text is not None and len(self.text) > 200:
            raise ValidationError({'text': 'Текст отзыва не должен превышать 200 символов'})

    def save(self, *args, **kwargs):
        if self.rating < 1 or self.rating > 5:
            raise ValidationError("Неверный рейтинг")
        super().save(*args, **kwargs)
