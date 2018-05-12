from rest_framework import serializers
from . import models

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = user
#         fields =(
#         'id',
#         'name',
#         'password',
#         )
#         extra_kwargs = {'password': {'write_only':True}}
#
#     def create(self, validated_data):
#         user = models.UserProfile(
#             name = validated_data['name'],
#         )
#         user.set_password(validated_data['password'])
#         user.save()
#         return user
class BaseModelSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
        'created_at',
        'updated_at'
        )


class MakeGym(objdect):
    def __init__(self, problems, users, name, description, slug):
        # self.problems = problems
        # self.users = users
        self.name = name
        self.description = description
        self.slug = slug

class GymSerializer(serializers.ModelSerializer):
    class Meta:
        fields=(
        'problems',
        'users',
        'name',
        'description',
        'slug'
        )
    extra_kwargs={'problems':{'read_only':True}, 'users':{'read_only':True}}
    def created(self, validated_data):
        return MakeGym(**validated_data)
class GymUserSerializer(serializers.ModelSerializer):
    class Meta:
        fields=(
        'gym',
        'user'
        )
    extra_kwargs={'gym':{'read_only':True}}

class GymProblem(serializers.ModelSerializer):
    class Meta:
        fields=(
        'gym',
        'problem',
        'order',
        'is_active'
        )
    extra_kwargs={'gym':{'read_only':True},'problem':{read_only:True}}
class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
        'type',
        'description',
        'judge_spec',
        'tags',
        'slug',
        )
    def create(self, validated_data):
        return Problem.objects.create(**validated_data)

class ProblemTagSerialzer(serializers.ModelSerializer):
    class Meta:
        fields=(
        'problem',
        'tag'
        )
    extra_kwargs={'problem':{'read_only':True},'tag':{'read_only':True}}

class JudgeSpecSerializer(serializers.ModelSerializer):
    class Meta:
        fields=(
        'type',
        'config',
        'mem_limit_bytes',
        'time_limit_seconds',
        'grader',
        'test_data'
        )
    def create(self, validated_data):
        return JudgeSpec.objects.create(**validated_data)

class Tag(object):
    def __init__(self, name, description):
        self.name = name
        self.description=description
class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields=(
        'name',
        'description'
        )
    def create(self, validated_data):
        return Tag.objects.create(**validated_data)

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        fields=(
        'user',
        'problem',
        'lang_profile',
        'submission_data'
        )
    extra_kwargs = {'user':{'read_only':True}, 'problem':{'read_only':True}}
    def create(self, validated_data):
        return Submission.objects.create(**validated_data)


class JudgeResultSerializer(serializers.ModelSerializer):
    class Meta:
        fields=(
        'submission',
        'status',
        'memory_used_bytes',
        'time_elapsed_seconds',
        'code_size',
        'score',
        'detail'
        )
    def create(self, validated_data):
        return JudgeResult.objects.create(**validated_data)
