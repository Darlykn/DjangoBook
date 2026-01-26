from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import CustomUser


class RegisterUserForm(UserCreationForm):
    """Форма регистрации пользователей"""
    name = forms.CharField(label='Имя', widget=forms.TextInput(attrs={'class': 'form-input'}))
    phone_number = forms.CharField(label='Номер телефона', widget=forms.TextInput(attrs={'class': 'form-input'}), initial='8')
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}), min_length=8,
                                error_messages={'min_length': 'Пароль должен быть длиной не менее 8 символов'})
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'user'

        if commit:
            user.save()
        return user

    class Meta:
        model = CustomUser  # Используем кастомную модель пользователя
        fields = ('name', 'phone_number', 'email', 'password1', 'password2')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-input'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-input'}),
        }


class LoginUserForm(AuthenticationForm):
    """Форма для аутентификации пользователей"""
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    def __init__(self, *args, **kwargs):
        super(LoginUserForm, self).__init__(*args, **kwargs)
        # Переопределение поля username на email
        self.fields['username'].label = 'Email'
        self.fields['username'].widget = forms.EmailInput(attrs={'class': 'form-input'})

