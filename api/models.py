from enum import Enum

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django_mysql.models import JSONField

from api.s3 import get_submission_path
from coding.custom_storages import MediaStorage


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


User.add_to_class(
    "name",
    property(lambda self: '%s%s' % (self.last_name, self.first_name))
)
User.add_to_class(
    "__str__",
    lambda self: '%s %s' % (self.last_name, self.first_name)
)


class Gym(BaseModel):
    problems = models.ManyToManyField('Problem', through='GymProblem')
    users = models.ManyToManyField(User, through='GymUser')
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'gym'
        verbose_name = '도장'
        verbose_name_plural = '도장'

    def __str__(self):
        return self.name


class GymUser(BaseModel):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'gym_user'


class GymProblem(BaseModel):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)
    problem = models.ForeignKey('Problem', on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'gym_problem'


class ProblemType(Enum):
    batch = 'Batch'
    reactive = 'Reactive'
    output_only = 'Output only'

    @classmethod
    def choices(cls):
        return [
            (p.value, p.name) for p in cls
        ]


class Problem(BaseModel):
    type = models.CharField(max_length=255, choices=ProblemType.choices())
    name = models.CharField(max_length=255)
    description = models.TextField()
    tags = models.ManyToManyField('Tag', through='ProblemTag')
    slug = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'problem'
        verbose_name = '문제'
        verbose_name_plural = '문제'

    def __str__(self):
        return self.name


class ProblemTag(BaseModel):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)

    class Meta:
        db_table = 'problem_tag'


class JudgeSpecType(Enum):
    batch = 'Batch'
    batch_with_grader = 'Batch with grader'
    output_only = 'Output only'

    @classmethod
    def choices(cls):
        return [
            (p.value, p.name) for p in cls
        ]


class JudgeSpec(BaseModel):
    problem = models.OneToOneField(
        'Problem', on_delete=models.CASCADE, related_name='judge_spec'
    )
    type = models.CharField(max_length=255, choices=JudgeSpecType.choices())
    config = JSONField()
    mem_limit_bytes = models.IntegerField()
    time_limit_seconds = models.IntegerField()

    grader = models.URLField()
    test_data = models.URLField()

    class Meta:
        db_table = 'judge_spec'
        verbose_name = '채점기준'
        verbose_name_plural = '채점기준'


class Tag(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    class Meta:
        db_table = 'tag'
        verbose_name = '태그'
        verbose_name_plural = '태그'

    def __str__(self):
        return self.name


class LanguageProfile(Enum):
    cpp = 'c++'
    java = 'java'
    python3 = 'python3'
    go = 'go'

    @classmethod
    def choices(cls):
        return [
            (p.value, p.name) for p in cls
        ]


class Submission(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    lang_profile = models.CharField(
        max_length=20, choices=LanguageProfile.choices()
    )

    submission_data = models.FileField(
        upload_to=get_submission_path, storage=MediaStorage()
    )

    class Meta:
        db_table = 'submission'
        verbose_name = '제출'
        verbose_name_plural = '제출'

    def __str__(self):
        return '%s 문제에 대한 %s 의 제출 (%s)' % (
            self.problem.name, self.user.name, self.lang_profile
        )


class JudgeStatus(Enum):
    enqueued = 'ENQ'
    in_progress = 'IP'
    compile_error = 'CTE'
    passed = 'PASS'
    failed = 'FAIL'
    internal_error = 'ERR'

    @classmethod
    def choices(cls):
        return [
            (p.value, p.name) for p in cls
        ]


class JudgeResult(BaseModel):
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=JudgeStatus.choices())
    memory_used_bytes = models.IntegerField()
    time_elapsed_seconds = models.IntegerField()
    code_size = models.IntegerField()
    score = models.IntegerField()
    detail = JSONField()

    class Meta:
        db_table = 'judge_result'
        verbose_name = '채점결과'
        verbose_name_plural = '채점결과'

    def __str__(self):
        return '%s 에 대한 채점결과 (%s)점' % (self.submission.__str__(), self.score)
