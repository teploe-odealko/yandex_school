from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.decorators import renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response


def custom404(request, exception=None):
    return JsonResponse({
        "code": 404,
        "message": "Item not found"
    }, status=404)


handler404 = custom404


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls')),
    path('__debug__/', include('debug_toolbar.urls'))
]

