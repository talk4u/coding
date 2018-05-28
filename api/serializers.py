from datetime import datetime, timedelta

from django.db.models import Max, Q
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

import api.models as models
from api.s3 import read_file
from api.utils import is_student


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ('id', 'name', 'username', 'email')


class ProblemSummarySerializer(serializers.ModelSerializer):
    max_score = SerializerMethodField()

    class Meta:
        model = models.Problem
        fields = ('id', 'name', 'max_score', 'slug')

    def get_max_score(self, obj):
        max_score = models.JudgeResult.objects.filter(
            submission__problem=obj,
            submission__user=self.context['request'].user
        ).aggregate(Max('score')).get('score__max', 0)
        return max_score if max_score else 0


class GymSerializer(serializers.ModelSerializer):
    problems = SerializerMethodField()
    recently_showed_users = SerializerMethodField()

    class Meta:
        model = models.Gym
        exclude = ('users', )

    def get_problems(self, obj):
        user = self.context['request'].user
        problems = obj.problems.all().order_by('gymproblem__order')
        problem_summary_list, zero_cnt = [], 0
        for problem in problems:
            problem_summary = ProblemSummarySerializer(
                problem, context=self.context
            ).data
            if problem_summary['max_score'] == 0:
                zero_cnt += 1

            problem_summary_list.append(problem_summary)

            if zero_cnt >= 3 and is_student(user):
                break

        return problem_summary_list

    def get_recently_showed_users(self, obj):
        queryset = models.JudgeResult.objects.filter(
            updated_at__gte=datetime.now()-timedelta(days=1),
            submission__problem__in=obj.problems.all()
        )
        user_ids = queryset.values_list(
            'submission__user_id', flat=True
        ).distinct()
        users = models.User.objects.filter(
            Q(id__in=user_ids) & ~Q(id=self.context['request'].user.id)
        )
        return UserSerializer(users, many=True).data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = '__all__'


class ProblemSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    mem_limit_bytes = serializers.IntegerField(
        source='judge_spec.mem_limit_bytes'
    )
    time_limit_seconds = serializers.IntegerField(
        source='judge_spec.time_limit_seconds'
    )

    class Meta:
        model = models.Problem
        fields = '__all__'


class ProblemRankSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(
        source='submission.user.username'
    )

    class Meta:
        model = models.JudgeResult
        fields = ('user_name', 'memory_used_bytes', 'time_elapsed_seconds',
                  'code_size', 'submission_id', 'created_at')


class SubmissionSerializer(serializers.ModelSerializer):
    submission_data = SerializerMethodField()

    class Meta:
        model = models.Submission
        fields = '__all__'

    @staticmethod
    def get_submission_data(obj):
        return read_file(obj.submission_data)
