from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework import viewsets
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import generics

from . import serailzsers
from . import models
from . import permissions

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

# Create your views here.
# class GymApiView(viewsets.Viewset):
#     serializer_class = serializers.GymSerializer
#     queryset = models.Gym.objects.all();
#
#     def create(self, request):
#         serializer = serializers.GymSerializer
#
#         if serializer.is_valid():
#             return Response(serializer.data)
#         else :
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
# class GymUserApiView(viewsets.ModelViewset):
#     serializer_class = serailzsers.GymUserSerializer
#     queryset = models.GymUser.objects.all()
#     authentication_classes = (TokenAuthentication,)
#     filter_backends = (filters.SearchFilter,)
#     search_fields= ('gym',)




class UserViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer


class GymViewSet(NestedViewSetMixin, ModelViewSet):
    serializer_class = serializers.GymSerializer

    def get_queryset(self):
        user = self.request.user
        gyms = models.Gym.objects.all()
        if user.groups.filter(name='student').exists():
            gyms = gyms.filter(users=user)
        return gyms

    def create(self, request):
        serializer = serializers.GymSerializer
        if serializer.is_valid():
            return Response(serializer.data)
        else :
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProblemViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = models.Problem.objects.all()
    serializer_class = serializers.ProblemSerializer
    def create(self, request):
        serializer = serializer.ProblemSerializer
        if serializer.is_valid():
            return Response(serailzer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TagViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


class SubmissionViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = models.Submission.objects.all()
    serializer_class = serializers.SubmissionSerializer
    def create(self, request):
        serailzer = serializers.SubmissionSerializer
        if serializer.is_valid():
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class JudgeResultViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = models.JudgeResult.objects.all()
    serializer_class = serailzsers.SubmissionSerializer
