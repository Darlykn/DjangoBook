from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError
import re


class CustomUserManager(BaseUserManager):
    """
       Менеджер пользовательских моделей, предоставляющий методы для создания пользователей и суперпользователей.
       Методы:
       - create_user: Создает и возвращает пользователя с обычными правами доступа.
       - create_superuser: Создает и возвращает пользователя с правами суперпользователя.
    """
    def create_user(self, email, password=None, role=None, phone_number=None, name=None):
        if role is None:
            role = 'user'
        user = self.model(
            email=self.normalize_email(email),
            role=role,
            phone_number=phone_number,
            name=name
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, role=None, phone_number=None, name=None):
        if role is None:
            role = 'admin'
        user = self.create_user(email, password, role, phone_number, name)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
        Модель CustomUser представляет собой пользователя системы.
        Атрибуты:
        - name: Имя пользователя. Ограничено 50 символами.
        - phone_number: Уникальный номер телефона пользователя. Должен содержать 11 цифр.
        - email: Уникальный электронный адрес пользователя. Ограничен 100 символами.
        - role: Роль пользователя в системе, может быть 'admin', 'manager', или 'user'.
        - is_active: Флаг, указывающий, является ли пользователь активным.
        - is_staff: Флаг, указывающий, имеет ли пользователь доступ к административной части сайта.
        - status: Статус пользователя, может быть пустым.

        Методы:
        - __str__: Возвращает имя пользователя.
        - has_perm: Определяет, имеет ли пользователь определённые разрешения в зависимости от своей роли.
        - has_module_perms: Определяет, имеет ли пользователь доступ к определённым модулям.
        - clean: Валидация полей перед сохранением.
        - save: Сохраняет пользователя, автоматически устанавливая is_staff в зависимости от роли и проводя
                полную валидацию данных.

        Мета-класс:
        - verbose_name: Читаемое название модели в единственном числе - 'пользователь'.
        - verbose_name_plural: Читаемое название модели во множественном числе - 'пользователи'.
        - ordering: Сортировка пользователей по электронной почте.
    """
    name = models.CharField(max_length=50, verbose_name='имя')
    phone_number = models.CharField(max_length=11, unique=True, verbose_name='номер телефона')
    email = models.EmailField(max_length=100, unique=True, verbose_name='email')
    ROLE_CHOICES = (
        ('admin', 'Администратор'),
        ('manager', 'Менеджер'),
        ('user', 'Пользователь')
    )
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='user', verbose_name="роль")
    is_active = models.BooleanField(default=True, verbose_name='активный')
    is_staff = models.BooleanField(default=False, verbose_name='статус персонала')
    status = models.CharField(max_length=20, blank=True, null=True, verbose_name='статус')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number', 'name']

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        if self.role == 'admin':
            return True  # Администраторы имеют все разрешения.
        if self.role == 'manager':
            # Проверка на разрешение изменения заказа.
            if perm in ['orders.change_order', 'orders.view_order']:
                return True
        return super().has_perm(perm, obj=obj)

    def has_module_perms(self, app_label):
        if self.role == 'admin':
            return True  # Администраторы имеют доступ ко всем модулям.
        if self.role == 'manager':
            # Менеджеры имеют доступ только к модулю 'orders'.
            return app_label == 'orders'
        return super().has_module_perms(app_label)

    def clean(self):
        super().clean()
        if self.name is not None and len(self.name) > 50:
            raise ValidationError({'name': 'Имя не должно превышать 50 символов.'})

        if self.email is not None and len(self.email) > 100:
            raise ValidationError({'email': 'Email не должен превышать 100 символов.'})

        if self.phone_number is not None and not re.match(r'^\d{11}$', self.phone_number):
            raise ValidationError({'phone_number': 'Номер телефона должен состоять из 11 цифр.'})

        if self.role and len(self.role) > 30:
            raise ValidationError({'role': 'Роль не должна превышать 30 символов.'})

        if self.status and len(self.status) > 20:
            raise ValidationError({'status': 'Статус не должен превышать 20 символов.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        # Автоматически устанавливаем is_staff на основе роли пользователя
        self.is_staff = self.role in {'admin', 'manager'}
        super(CustomUser, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ['email']

