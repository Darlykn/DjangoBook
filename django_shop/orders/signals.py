from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderProduct

@receiver(post_save, sender=OrderProduct)
def update_order_total_on_save(sender, instance, **kwargs):
    instance.id_order.update_total_cost()

@receiver(post_delete, sender=OrderProduct)
def update_order_total_on_delete(sender, instance, **kwargs):
    instance.id_order.update_total_cost()
