"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.settings import api_settings

V1 = "api/v1"

urlpatterns = [
    path("admin/", admin.site.urls),
    # Open API & Swagger UI
    path(
        "api/openapi",
        SpectacularAPIView.as_view(
            renderer_classes=api_settings.DEFAULT_RENDERER_CLASSES
        ),
        name="openapi",
    ),
    path(
        "api/docs",
        SpectacularSwaggerView.as_view(url_name="openapi"),
        name="swagger-ui",
    ),
    path("api/redoc", SpectacularRedocView.as_view(url_name="openapi"), name="redoc"),
    path(
        "",
        SpectacularSwaggerView.as_view(url_name="openapi"),
        name="swagger-ui",
    ),
    path(f"{V1}/weather/", include("weather.urls")),
]
