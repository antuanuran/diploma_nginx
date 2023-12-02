from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.basket.views import BasketRowViewSet

router = DefaultRouter()
router.register("basket-rows", BasketRowViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
