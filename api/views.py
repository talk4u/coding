from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets

from . import serailzsers
from . import models

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

# Create your views here.
class GymApiView(viewsets.Viewset):
    serializer_class = serializers.GymSerializer
    queryset = models.Gym.objects.all();

    def list(self, request):
        return Response()
