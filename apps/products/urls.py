from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.products.views import ItemViewSet, import_data, import_file

router = DefaultRouter()
router.register("items", ItemViewSet)

urlpatterns = [
    path("products-import-data/", import_data),
    path("products-import-file/", import_file),
    path("", include(router.urls)),
]
