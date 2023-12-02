from rest_framework import serializers

from apps.products.models import Item, ItemParameter, Product, Vendor, Category


class VendorSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(slug_field="email", read_only=True)

    class Meta:
        model = Vendor
        fields = ["id", "name", "owner"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    vendor = VendorSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "category", "vendor"]


class ItemParameterSerializer(serializers.ModelSerializer):
    attribute = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = ItemParameter
        fields = ["attribute", "value"]


class ItemSerializer(serializers.ModelSerializer):
    tovar_id = serializers.IntegerField(source="id")

    class Meta:
        model = Item
        fields = [
            "tovar_id",
            "product",
            "price",
            "count",
            "upc",
            "parameters",
        ]


class DetailItemSerializer(ItemSerializer):
    product = serializers.SlugRelatedField(slug_field="name", read_only=True)
    parameters = ItemParameterSerializer(read_only=True, many=True)
