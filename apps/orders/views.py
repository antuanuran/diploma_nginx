from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet
from django.db import transaction
from drf_yasg.utils import no_body, swagger_auto_schema

from apps.orders.models import Order
from apps.orders.premissions import IsOwner
from apps.orders.serializers import OrderSerializer
from rest_framework import status
from django.utils.decorators import method_decorator


@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        operation_description='Менять статус заказа "status" можно только на "отменен" ',
    ),
)
class OrderViewSet(ModelViewSet):
    http_method_names = [
        "get",
        "post",
        "head",
        "options",
        "patch",
    ]  # Get на сущность, Get на список, Patch на сущность. Post - разрешили, но сам create - нужно запретить

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        qs = super().get_queryset()
        result = qs.filter(user_id=self.request.user.id)
        return result

    @swagger_auto_schema(auto_schema=None)
    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # detail-False означает, что мы работаем со всем списком, а не с конкретной сущностью
    @swagger_auto_schema(request_body=no_body)
    @action(methods=["post"], detail=False)
    def checkout(self, request):
        user = request.user
        basket = request.user.baskets.first()

        if not basket:
            raise ValidationError("user hasn't basket", code="no-basket")

        if not basket.rows.exists():
            raise ValidationError("user hasn't products in the basket", code="no-products-in-basket")

        for row in basket.rows.all():
            if row.qty > row.item.count:
                raise ValidationError(f"item is out of stock - {row.item.product.name}", code="no-products-in-basket")

            if not row.item.is_active:
                raise ValidationError(
                    f"На текущий момент - Товар:{row.item.product.name} отсутствует а складе",
                    code="no-products",
                )

        # транзакция - для безопасного кода
        with transaction.atomic():
            order = Order.objects.create(user=user)
            for row in basket.rows.all():
                order.rows.create(item=row.item, qty=row.qty, price=row.item.price)
            basket.rows.all().delete()  # Очищаем корзину
        ### транзакция завершена

        serializer = OrderSerializer(order)  # Выводим через сериализатор итог покупок
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
