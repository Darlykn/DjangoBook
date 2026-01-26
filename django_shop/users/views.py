from loguru import logger

from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView
from .forms import RegisterUserForm, LoginUserForm
from .utils import DataMixin


logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB")


class RegisterUser(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'shop/product/register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_context = self.get_user_context(title='Регистрация')
        context['form_first'] = RegisterUser.form_class
        return dict(list(context.items()) + list(user_context.items()))

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('shop:product_list')


class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'shop/product/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user_context = self.get_user_context(title='Войти')
        return dict(list(context.items()) + list(user_context.items()))

    def get_success_url(self):
        return reverse_lazy('shop:product_list')


def logout_user(request):
    logout(request)  # стандартная ф-ия Джанго для выхода из авторизации
    return redirect('users:login')
