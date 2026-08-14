from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("product.urls")),
    path("api/", include("order.urls")),
] + debug_toolbar_urls()
