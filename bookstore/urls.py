from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from bookstore.views import hello_world, update_server


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("product.urls")),
    path("api/", include("order.urls")),
    path("hello/", hello_world, name="hello-world"),
    path("update_server/", update_server, name="deploy-webhook"),
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
