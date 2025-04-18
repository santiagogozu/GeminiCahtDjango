from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("agent.urls")),
    path("", include("agent.urls")),  # asegúrate de incluir aquí tu app
]
