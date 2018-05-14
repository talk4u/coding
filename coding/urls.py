from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

from rest_framework_swagger.views import get_swagger_view

import api.urls

schema_view = get_swagger_view(title='Coding API')

urlpatterns = [
    path('api/', include(api.urls)),
    path('admin/', admin.site.urls),
    path('ping/', lambda r: HttpResponse("pong")),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('docs/', schema_view),
]
