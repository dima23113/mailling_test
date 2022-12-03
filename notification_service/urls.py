from django.contrib import admin
from django.urls import path, include

from .routers import router
from .yasg import swagger_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/api-auth/', include("rest_framework.urls", namespace="rest_framework")),
    path('api/v1/', include(router.urls)),
]

urlpatterns += swagger_urlpatterns
