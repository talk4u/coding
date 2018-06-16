from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin

import api.models as models
import api.serializers as serializers
from api.permissions import IsOwnerOrSolverOrInstructor, IsOwnerOrInstructor
from api.utils import is_student, is_instructor, update_dict_in_exist_keys, \
    get_latest_judge_result_queryset


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
    queryset = get_latest_judge_result_queryset(
        models.JudgeResult.objects.filter(
            status=models.JudgeStatus.PASSED.value,
            score=100
        )
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

    @detail_route(methods=['get'], url_path='detail')
    def get_submission_detail(self, request, pk, parent_lookup_problem):
        submission = models.Submission.objects.get(pk=pk)
        return Response(
            serializers.SubmissionForJudgeSerializer(submission).data
        )

    @detail_route(methods=['post'], url_path='rejudge')
    def request_submission_rejudge(self, request, pk, parent_lookup_problem):
        # TODO : call JudgeRequest to Treadmill
        pass

    def perform_create(self, serializer):
        code_size = serializer.validated_data['submission_data'].size
        serializer.save(user=self.request.user, code_size=code_size)


class JudgeResultViewSet(NestedViewSetMixin, ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,
                          IsOwnerOrInstructor,)

    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('status',)

    def get_queryset(self):  # pragma: no cover
        user = self.request.user
        qs = models.JudgeResult.objects.all() if is_instructor(user) \
            else models.JudgeResult.objects.filter(submission__user=user)
        qs = self.filter_queryset_by_parents_lookups(qs)
        results = get_latest_judge_result_queryset(qs)
        return results.order_by('-created_at')

    def get_serializer_class(self):  # pragma: no cover
        if self.action is 'retrieve':
            return serializers.JudgeResultDetailSerializer
        else:
            return serializers.JudgeResultSerializer


class JudgeViewSet(ModelViewSet):
    queryset = models.JudgeResult.objects.all()
    serializer_class = serializers.JudgeResultSerializer

    @detail_route(
        methods=['patch'],
        url_path='testset/(?P<testset_id>[0-9]+)'
                 '/testcase/(?P<testcase_id>[0-9]+)'
    )
    def put_testcase_judge_result(
            self, request, pk, testset_id, testcase_id
    ):  # pragma: no cover
        judge_result = models.JudgeResult.objects.get(pk=pk)

        partial_data = request.data
        updated_testsets = []
        for testset in judge_result.detail:
            updated_testcases = []
            for testcase in testset['testcases']:
                if int(testset['id']) == int(testset_id) and \
                                int(testcase['id']) == int(testcase_id):
                    testcase = update_dict_in_exist_keys(
                        testcase, partial_data
                    )
                updated_testcases.append(testcase)
            testset['testcases'] = updated_testcases
            updated_testsets.append(testset)

        judge_result.detail = updated_testsets
        judge_result.save()

        return Response(
            serializers.JudgeResultDetailSerializer(judge_result).data
        )

    @detail_route(methods=['patch'], url_path='testset/(?P<testset_id>[0-9]+)')
    def put_testset_judge_result(
            self, request, pk, testset_id
    ):  # pragma: no cover
        judge_result = models.JudgeResult.objects.get(pk=pk)

        partial_data = request.data
        updated_testsets = []
        for testset in judge_result.detail:
            if int(testset['id']) == int(testset_id):
                testset = update_dict_in_exist_keys(testset, partial_data)
            updated_testsets.append(testset)

        judge_result.detail = updated_testsets
        judge_result.save()

        return Response(
            serializers.JudgeResultDetailSerializer(judge_result).data
        )
