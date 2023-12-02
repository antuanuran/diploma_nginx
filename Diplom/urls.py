from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("docs/", include("Diplom.urls_docs")),
    path("api/v1/auth/", include("djoser.urls")),
    path("api/v1/auth/", include("djoser.urls.jwt")),
    path("api/v1/", include("apps.products.urls")),
    path("api/v1/", include("apps.basket.urls")),
    path("api/v1/", include("apps.orders.urls")),
]
