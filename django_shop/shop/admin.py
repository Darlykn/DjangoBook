from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Product, Category, Review


class OrderReviewInline(admin.TabularInline):
    model = Review
    extra = 0  # чтобы не отображать пустые строки по умолчанию


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'id_category', 'price', 'quantity', 'get_html_photo']
    list_filter = ['id_category']
    ordering = ['title']
    search_fields = ['title', 'author']
    inlines = [OrderReviewInline]  # связываем отзывы с товарами

    #  метод для отображения миниатюр в админке
    def get_html_photo(self, object):  # object тут ссылается на запись из таблицы (ЭК модели Product)
        if object.image:
            return mark_safe(
                f"<img src='{object.image.url}' width=65>")  # ф-ия mark_safe позволяет не экранировать то, что мы в нее передаем

    get_html_photo.short_description = 'Миниатюра '

