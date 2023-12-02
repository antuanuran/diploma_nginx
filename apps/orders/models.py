from django.utils import timezone
from django.core.exceptions import ValidationError


from django.db import models

from apps.products.models import Item
from apps.users.models import User


class Order(models.Model):
    STATUS_NEW = "новый"
    STATUS_DELIVERY = "в доставке"
    STATUS_FINISHED = "завершен"
    STATUS_CANCELED = "отменен"

    STATUSES = [
        (STATUS_NEW, "новый"),
        (STATUS_DELIVERY, "в доставке"),
        (STATUS_FINISHED, "завершен"),
        (STATUS_CANCELED, "отменен"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    items = models.ManyToManyField(Item, through="OrderRow", related_name="orders", blank=True)
    status = models.CharField(max_length=30, choices=STATUSES, default=STATUS_NEW)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    # rows

    @property
    def sum_total_all_orders(self):
        total = 0
        for row in self.rows.all():
            total += row.sum_current_order
        return total

    @property
    def number_order(self):
        text = f"Заказ № {self.id}"
        return text

    class Meta:
        verbose_name = "Покупка"
        verbose_name_plural = "Покупки"

    def __str__(self):
        return self.user.email


class OrderRow(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="rows")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="order_rows")
    qty = models.PositiveIntegerField()
    price = models.PositiveIntegerField()

    @property
    def sum_current_order(self):
        return (self.qty or 0) * (self.price or 0)

    # ******************************
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        if not self.item.is_active:
            raise ValidationError({"item not active!"}, code="not-active-item")

    # ******************************

    class Meta:
        verbose_name = "Покупка"
        verbose_name_plural = "Покупки"

    def __str__(self):
        return f"Товар: {self.item}"
