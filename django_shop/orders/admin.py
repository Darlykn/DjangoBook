from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from .models import Order, OrderProduct


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    can_delete = True  # Изначально разрешаем удаление

    def get_readonly_fields(self, request, obj=None):
        if request.user.role == 'manager':
            return ['id_product', 'quantity']
        return []

    def has_change_permission(self, request, obj=None):
        if request.user.role == 'admin':
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.role == 'admin':
            return True
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'id_user', 'address', 'created_date', 'status']
    list_filter = ['created_date', 'status']
    list_editable = ['status']
    inlines = [OrderProductInline]

    def get_list_editable(self, request):
        if request.user.role == 'manager':
            return ['status']
        return []

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'manager' or request.user.is_superuser:
            return qs
        return qs.none()

    def get_readonly_fields(self, request, obj=None):
        if request.user.role == 'manager':
            return [field.name for field in self.model._meta.fields if field.name != 'status']
        return super().get_readonly_fields(request, obj)

    def has_change_permission(self, request, obj=None):
        if request.user.role == 'manager':
            return True
        return super().has_change_permission(request, obj=obj)

    def has_add_permission(self, request):
        if request.user.role == 'manager':
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        if request.user.role == 'manager':
            return False
        return super().has_delete_permission(request, obj=obj)

    def has_view_permission(self, request, obj=None):
        if request.user.role == 'manager':
            return True
        return super().has_view_permission(request, obj=obj)

    def changelist_view(self, request, extra_context=None):
        self.list_editable = self.get_list_editable(request)
        return super().changelist_view(request, extra_context)

    def save_model(self, request, obj, form, change):
        if change:  # Если это изменение существующего объекта
            old_obj = Order.objects.get(pk=obj.pk)
            valid_transitions = {
                'wait': ['processing'],
                'processing': ['shipped'],
                'shipped': ['delivered'],
                'delivered': []
            }
            if old_obj.status != obj.status and obj.status not in valid_transitions[old_obj.status]:
                self.message_user(
                    request,
                    _('Невозможно изменить статус с %(old_status)s на %(new_status)s.') % {
                        'old_status': old_obj.get_status_display(),
                        'new_status': obj.get_status_display(),
                    },
                    messages.ERROR
                )
                return  # Остановить сохранение объекта и не выводить сообщение об успешном изменении
        super().save_model(request, obj, form, change)

    def response_change(self, request, obj):
        if "_save" in request.POST:
            if obj.status in ['shipped', 'delivered'] and obj.status in ['wait', 'processing']:
                return HttpResponseRedirect(request.path)
        return super().response_change(request, obj)
