from django.db import models
from django.core.exceptions import ValidationError


from apps.products.models import Item
from apps.users.models import User


class Basket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="baskets")
    items = models.ManyToManyField(Item, through="BasketRow", related_name="baskets", blank=True)
    # rows

    @property
    def total_price_all_basket(self):
        total = 0
        for row in self.rows.all():
            total += row.summa_price
        return total

    @property
    def number_baskets(self):
        text = f"Корзина ({self.user})"
        return text

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return self.user.email


class BasketRow(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name="rows")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="basket_rows")
    qty = models.PositiveIntegerField(default=1)

    @property
    def summa_price(self):
        return self.qty * self.item.price

    @property
    def price_unit(self):
        return self.item.price

    @property
    def is_active_item(self):
        if self.item.is_active:
            return "Yes"
        else:
            return "Not"

    # ******************************
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        if not self.item.is_active:
            raise ValidationError({"item not active!"}, code="not-active-item")

    # ******************************

    class Meta:
        verbose_name = "Заказ в корзине"
        verbose_name_plural = "Заказы в корзине"

    def __str__(self):
        return f" {self.item}"
