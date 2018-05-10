from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

from rest_framework_jwt.views import obtain_jwt_token

import api.urls

urlpatterns = [
    path('api/', include(api.urls)),
    path('admin/', admin.site.urls),
    path('ping/', lambda r: HttpResponse("pong")),
    path('api-token-auth/', obtain_jwt_token),
]
