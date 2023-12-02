from rest_framework import serializers
from apps.orders.models import OrderRow, Order
from apps.products.serializers import ItemSerializer, ItemParameterSerializer, ProductSerializer
from rest_framework.exceptions import PermissionDenied


class OrderDetailSerializer(ItemSerializer):
    parameters = ItemParameterSerializer(read_only=True, many=True)
    product = serializers.SlugRelatedField(slug_field="name", read_only=True)


class OrderRowSerializer(serializers.ModelSerializer):
    item = OrderDetailSerializer(read_only=True)

    class Meta:
        model = OrderRow
        fields = ["qty", "price", "item"]


class OrderSerializer(serializers.ModelSerializer):
    spisok_tovarov_zakaza = OrderRowSerializer(read_only=True, many=True, source="rows")
    order_id = serializers.IntegerField(source="id")

    class Meta:
        model = Order
        fields = [
            "order_id",
            "status",
            "created_at",
            "updated_at",
            "spisok_tovarov_zakaza",
        ]

    def validate_status(self, value):
        if value != Order.STATUS_CANCELED:
            raise PermissionDenied("User может изменять статус заказа только на 'отменён'")
        return value
