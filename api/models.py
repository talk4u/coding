from enum import Enum

from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class CustomUser(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = 'user'


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Team(BaseModel):
    team_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name='이름')
    description = models.TextField(verbose_name='설명')

    class Meta:
        db_table = 'team'
        verbose_name = '무리'
        verbose_name_plural = '무리'

    def __str__(self):
        return self.name


class Notice(BaseModel):
    notice_id = models.AutoField(primary_key=True)
    content = models.TextField()
    read_count = models.IntegerField()

    class Meta:
        db_table = 'notice'


class Palestra(BaseModel):
    palestra_id = models.AutoField(primary_key=True)
    team = models.ForeignKey('Team', on_delete=models.CASCADE)
    problems = models.ManyToManyField('Problem', through='PalestraProblem')
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'palestra'


class PalestraProblem(BaseModel):
    palestra_problem_id = models.AutoField(primary_key=True)
    palestra = models.ForeignKey(Palestra, on_delete=models.CASCADE)
    problem = models.ForeignKey('Problem', on_delete=models.CASCADE)
    order = models.IntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'palestra_problem'


class Notification(BaseModel):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    expired_date = models.DateTimeField()
    redirect_url = models.URLField()

    class Meta:
        db_table = 'notification'


class ProblemType(str, Enum):
    batch = 'Batch'
    reactive = 'Reactive'
    output_only = 'Output only'


class ProblemStatus(str, Enum):
    in_progress = 'In progress'
    in_testing = 'In testing'
    done = 'Done'


class Problem(BaseModel):
    problem_id = models.AutoField(primary_key=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=255,
        choices = [
            (e.value, e.name)
            for e in list(ProblemType)
        ]
    )
    description = models.TextField()
    data_set = models.OneToOneField('DataSet', on_delete=models.SET_NULL, blank=True, null=True)
    tags = models.ManyToManyField('Tag', through='ProblemTag')
    status = models.CharField(
        max_length=255,
        choices = [
            (e.value, e.name)
            for e in list(ProblemStatus)
        ]
    )
    slug = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'problem'


class ProblemTag(BaseModel):
    problem_tag_id = models.AutoField(primary_key=True)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)

    class Meta:
        db_table = 'problem_tag'


class RecommendedProblem(BaseModel):
    recommended_problem_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    class Meta:
        db_table = 'recommended_problem'


class DataSetType(str, Enum):
    batch = 'Batch'
    batch_with_grader = 'Batch with grader'
    output_only = 'Output only'


class DataSet(BaseModel):
    data_set_id = models.AutoField(primary_key=True)
    type = models.CharField(
        max_length=255,
        choices = [
            (e.value, e.name)
            for e in list(DataSetType)
        ]
    )
    time_limit = models.IntegerField()
    memory_limit = models.IntegerField()
    grading_info = models.TextField()
    grader_source = models.URLField()
    test_data = models.URLField()

    class Meta:
        db_table = 'data_set'


class Tag(BaseModel):
    tag_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    class Meta:
        db_table = 'tag'


class LanguageType(str, Enum):
    cpp = 'c++'
    cpp11 = 'c++11'
    cpp14 = 'c++14'
    cpp17 = 'c++17'
    python2 = 'python2'
    python3 = 'python3'
    pypy = 'pypy'
    pypy3 = 'pypy3'
    java = 'java'
    go = 'go'


class Submission(BaseModel):
    submission_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    language = models.CharField(
        max_length=255,
        choices = [
            (e.value, e.name)
            for e in list(LanguageType)
        ]
    )
    submission_data = models.URLField()

    class Meta:
        db_table = 'submission'


class SubmissionResultStatus(str, Enum):
    in_queue = 'In queue'
    judging = 'Judging'
    wrong_answer = 'Wrong answer'
    time_limit_exceed = 'Time limit exceed'
    memory_limit_exceed = 'Memory limit exceed'
    runtime_error = 'Runtime error'
    accepted = 'Accepted'


class SubmissionResult(BaseModel):
    result_id = models.AutoField(primary_key=True)
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=255,
        choices = [
            (e.value, e.name)
            for e in list(SubmissionResultStatus)
        ]
    )
    memory = models.IntegerField()
    time = models.IntegerField()
    code_size = models.IntegerField()
    score = models.IntegerField()
    compiled_message = models.TextField()
    detail = models.TextField()

    class Meta:
        db_table = 'submission_result'


class Channel(BaseModel):
    channel_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    class Meta:
        db_table = 'channel'


class Thread(BaseModel):
    thread_id = models.AutoField(primary_key=True)
    channel_id = models.ForeignKey(Channel, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message_body = models.TextField()

    class Meta:
        db_table = 'thread'
