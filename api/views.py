from rest_framework import filters, permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin

import api.models as models
import api.serializers as serializers
from api.permissions import IsOwnerOrSolverOrInstructor
from api.utils import is_student


class UserViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer


class GymViewSet(NestedViewSetMixin, ModelViewSet):
    serializer_class = serializers.GymSerializer

    def get_queryset(self):
        user = self.request.user
        gyms = models.Gym.objects.all()
        if is_student(user):
            gyms = gyms.filter(users=user)
        return gyms


class RankViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = models.JudgeResult.objects.filter(
        status=models.JudgeStatus.passed.value,
        score=100
    )
    serializer_class = serializers.ProblemRankSerializer
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = (
        'memory_used_bytes', 'time_elapsed_seconds', 'code_size', 'created_at'
    )
    ordering = ('created_at',)


class ProblemViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = models.Problem.objects.all()
    serializer_class = serializers.ProblemSerializer


class TagViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


class SubmissionViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = models.Submission.objects.all()
    serializer_class = serializers.SubmissionSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsOwnerOrSolverOrInstructor,)
