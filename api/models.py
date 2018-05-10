from enum import Enum

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django_mysql.models import JSONField


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

User.add_to_class("get_name", lambda self: '%s%s' % (self.last_name, self.first_name))
User.add_to_class("__str__", lambda self: '%s %s' % (self.last_name, self.first_name))


class Gym(BaseModel):
    problems = models.ManyToManyField('Problem', through='GymProblem')
    users = models.ManyToManyField(User, through='GymUser')
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'gym'


class GymUser(BaseModel):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'gym_user'


class GymProblem(BaseModel):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)
    problem = models.ForeignKey('Problem', on_delete=models.CASCADE)
    order = models.IntegerField()
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
    description = models.TextField()
    judge_spec = models.OneToOneField('JudgeSpec', on_delete=models.SET_NULL, blank=True, null=True)
    tags = models.ManyToManyField('Tag', through='ProblemTag')
    slug = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'problem'


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
    type = models.CharField(max_length=255, choices=JudgeSpecType.choices())
    config = JSONField()
    mem_limit_bytes = models.IntegerField()
    time_limit_seconds = models.IntegerField()

    grader = models.URLField()
    test_data = models.URLField()

    class Meta:
        db_table = 'judge_spec'


class Tag(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    class Meta:
        db_table = 'tag'


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
    lang_profile = models.CharField(max_length=20, choices=LanguageProfile.choices())

    submission_data = models.URLField()

    class Meta:
        db_table = 'submission'


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

