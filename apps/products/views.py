from django.utils.decorators import method_decorator
from rest_framework.parsers import MultiPartParser
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from drf_yasg import openapi

from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import LimitOffsetPagination

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.products.models import Item
from apps.products.serializers import DetailItemSerializer, ItemSerializer
from apps.users.permissions import IsVendor
from apps.products import service_HTTP
from apps.products import service


# Отключаем данный метод для swagger
@swagger_auto_schema(
    methods=["post", "get"],
    auto_schema=None,
)
@api_view(http_method_names=["post", "get"])
@permission_classes([IsAuthenticated, IsVendor])
def import_data(request):
    if request.method == "GET":
        item = Item.objects.first()

        return Response(
            data={
                "user": request.user.id,
                "file_name": request.query_params.get("file_name"),
                "name_product": item.product.name,
                "detail_data": ItemSerializer(item).data,
            }
        )

    name_format = request.query_params.get("file_name", "name.csv")
    list(name_format)

    name_file, data_format = name_format.rsplit(".")
    owner_id = request.user.id

    try:
        service_HTTP.import_data(name_file, data_format, owner_id)
    except FileNotFoundError:
        raise ValidationError("incorrect file name", code="incorrect-file-name")

    return Response(
        data=f"file: '{name_format}' LOAD......ok", status=status.HTTP_201_CREATED
    )


# 2-декоратора для swagger (загрузка через файл) @swagger_auto_schema+@parser_classes
@swagger_auto_schema(
    method="post",
    operation_description="Allowed only for vendors",
    manual_parameters=[
        openapi.Parameter(
            name="file",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            required=True,
            description="YAML or CSV",
        )
    ],
    responses={status.HTTP_201_CREATED: "result"},
)
@api_view(http_method_names=["post"])
@permission_classes([IsAuthenticated, IsVendor])
@parser_classes([MultiPartParser])
def import_file(request):
    if not request.FILES or "file" not in request.FILES:
        raise ValidationError("no file", code="no-file")

    data_stream = request.FILES["file"]
    _, data_format = data_stream.name.rsplit(".")

    if data_format == "csv":
        data_stream = data_stream.read().decode()
        service.import_http_csv(data_stream, request.user.id)
    else:
        service.import_data(data_stream, data_format, request.user.id)
    return Response(
        data=f"file: '{request.FILES['file'].name}' LOAD......ok",
        status=status.HTTP_201_CREATED,
    )


# Декораторы для swagger (убрать замок)
@method_decorator(name="list", decorator=swagger_auto_schema(security=[]))
@method_decorator(name="retrieve", decorator=swagger_auto_schema(security=[]))
class ItemViewSet(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = DetailItemSerializer
    http_method_names = ["get", "options", "head"]
    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    ]  # DjangoFilterBackend - сортировка по параметру. Не указали конкретный параметр, поэтому можно сортировать по всем параметрам нашей модели - Item

    filterset_fields = ["product__category"]  # Фильтр по id Категории
    search_fields = ["product__name"]
    pagination_class = LimitOffsetPagination

    # Добавляем декоратор для Swagger (чтобы убрать замок)
    # @swagger_auto_schema(security=[])
    # def list(self, request, *args, **kwargs):
    #     return super().list(request, *args, **kwargs)
