from rest_framework import serializers

from apps.basket.models import BasketRow, Item
from apps.products.serializers import ItemSerializer, ItemParameterSerializer, ProductSerializer
from rest_framework.exceptions import ValidationError


class BasketDetailSerializer(ItemSerializer):
    parameters = ItemParameterSerializer(read_only=True, many=True)
    product = serializers.SlugRelatedField(slug_field="name", read_only=True)


class BasketRowSerializer(serializers.ModelSerializer):
    item = BasketDetailSerializer(read_only=True)
    tovar_id = serializers.IntegerField(write_only=True, source="item_id")
    qty = serializers.IntegerField()

    class Meta:
        model = BasketRow
        fields = ["basket_id", "qty", "item", "tovar_id"]

    def validate(self, attrs):
        if not Item.objects.filter(id=attrs["item_id"], is_active=True).exists():
            raise ValidationError("incorrect item_id", code="no-item_id")
        else:
            return attrs

    def create(self, validated_data):
        # print(f"3. create - сериалайзер {validated_data}")

        item_id = validated_data["item_id"]
        basket_id = validated_data["basket_id"]

        exist_row = BasketRow.objects.filter(item_id=item_id, basket_id=basket_id).first()
        if exist_row:
            new_qty = exist_row.qty + validated_data["qty"]
            if new_qty > exist_row.item.count:
                raise ValidationError(f"too many items! Total: {exist_row.item.count}")

            exist_row.qty = new_qty
            exist_row.save()
            return exist_row

        item = Item.objects.get(id=validated_data["item_id"])
        if validated_data["qty"] > item.count:
            raise ValidationError(f"too many items! Total: {item.count}")

        return super().create(validated_data)
