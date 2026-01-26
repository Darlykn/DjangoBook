from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.contrib.auth.models import Group, User

# Отменить регистрацию стандартных моделей "Пользователи" и "Группы"
admin.site.unregister(Group)


@admin.register(CustomUser)
class CustomUser(UserAdmin):
    model = CustomUser
    list_display = ('email', 'name', 'phone_number', 'role', 'is_active', 'is_staff')
    list_filter = ('is_staff', 'is_active', 'role')
    fieldsets = (
        (None, {'fields': ('email', 'password', 'name', 'phone_number', 'role', 'is_active', 'is_staff', 'is_superuser')}
         ),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'name', 'phone_number', 'role', 'is_active', 'is_staff')}
         ),
    )
    search_fields = ('email', 'name', 'phone_number')
    ordering = ('email',)

