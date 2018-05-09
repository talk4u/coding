from rest_framework.viewsets import ModelViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin

import api.models as models
import api.serializers as serializers


class UserViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer


class GymViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = models.Gym.objects.all()
    serializer_class = serializers.GymSerializer


class ProblemViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = models.Problem.objects.all()
    serializer_class = serializers.ProblemSerializer


class TagViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


class SubmissionViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = models.Submission.objects.all()
    serializer_class = serializers.SubmissionSerializer
