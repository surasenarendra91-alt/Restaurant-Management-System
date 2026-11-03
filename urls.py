from django.contrib import admin
from django.urls import include, path

from restaurant.views import dashboard

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("admin/", admin.site.urls),
    path("api/", include("restaurant.urls")),
]
