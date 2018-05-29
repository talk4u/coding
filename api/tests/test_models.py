from django.test import TestCase

# Create your tests here.

from api.models import User, Gym, GymProblem, JudgeResult, JudgeSpec, Problem, Submission, Tag


class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        User.objects.create(first_name='승용', last_name='이')

    def test_first_name_label(self):
        user = User.objects.get(id=1)
        field_label = user._meta.get_field('first_name').verbose_name
        self.assertEquals(field_label, '이름')

    def test_last_name_label(self):
        user = User.objects.get(id=1)
        field_label = user._meta.get_field('last_name').verbose_name
        self.assertEquals(field_label, '성')

    def test_first_name_max_length(self):
        user = User.objects.get(id=1)
        max_length = user._meta.get_field('first_name').max_length
        self.assertEquals(max_length, 30)

    def test_object_name_is_last_name_space_first_name(self):
        user = User.objects.get(id=1)
        expected_object_name = '%s %s' % (user.last_name, user.first_name)
        self.assertEquals(expected_object_name, str(user))

    def test_get_name(self):
        user = User.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        user_name = '%s%s' % (user.last_name, user.first_name)
        self.assertEquals(user.name, user_name)

class GymModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Gym.objects.create(name= '도장 1', description= 'activated for test', slug= 'A')

    def test_gym_label(self):
        verbose = Gym._meta.verbose_name.title()
        self.assertEquals(verbose, '도장' )

    def test_gym_plural_label(self):
        verbose = Gym._meta.verbose_name_plural.title()
        self.assertEquals(verbose, '도장' )

    def test_gym_name(self):
        gym= Gym.objects.get(id=1)
        field_label = gym._meta.get_field('name')
        self.assertEquals(field_label, '도장 1')

    def test_gym_name_max_length(self):
        gym= Gym.objects.get(id=1)
        max_length = gym._meta.get_field('name').max_length
        self.assertEquals(max_length, 255)

    def test_gym_description(self):
        gym= Gym.objects.get(id=1)
        field_label = gym._meta.get_field('description')
        self.assertEquals(field_label, 'activated for test')

    def test_gym_description_max_length(self):
        gym= Gym.objects.get(id=1)
        max_length = gym._meta.get_field('description').max_length
        self.assertEquals(max_length, 255)

    def test_gym_slug(self):
        gym = Gym.objects.get(id=1)
        field_label = gym._meta.get_field('slug')
        self.assertEquals(field_label, 'A')

    def test_gym_description_max_length(self):
        gym= Gym.objects.get(id=1)
        max_length = gym._meta.get_field('slug').max_length
        self.assertEquals(max_length, 255)

# class GymProblemTest(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         GymProblem.objects.create(order =1, is_active=True)
#
#     def test_gym_prob_order(self):
#         gymprob = GymProblem.objects.get(id=1)
#         field_label = gymprob._meta.get_field('order')
#         self.assertEquals(field_label, 1)
#
#     def test_gym_prob_isactive(self):
#         gymprob = GymProblem.objects.get(id=1)
#         field_label = gymprob._meta.get_field('is_active')
#         self.assertEquals(field_label, True)

class ProblemTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Problem.objects.create(type='problem type 1', name='problem 1', description='what up?', slug='AB' )

    def test_problem_label(self):
        verbose = Problem._meta.verbose_name.title()
        self.assertEquals(verbose, '문제')

    def test_problem_plural_label(self):
        verbose = Problem._meta.verbose_name_plural.title()
        self.assertEquals(verbose, '문제')

    def test_problem_type(self):
        problem = Problem.objects.get(id=1)
        field_label = problem._meta.get_field('type')
        self.assertEquals(field_label, 'problem type 1')

    def test_problem_type_max_length(self):
        problem = Problem.objects.get(id=1)
        max_length = problem._meta.get_field('type').max_length
        self.assertEquals(max_length, 255)

    def test_problem_name(self):
        problem = Problem.objects.get(id=1)
        field_label = problem._meta.get_field('name')
        self.assertEquals(field_label, 'problem 1')

    def test_problem_type_max_length(self):
        problem = Problem.objects.get(id=1)
        max_length = problem._meta.get_field('name').max_length
        self.assertEquals(max_length, 255)

    def test_problem_type(self):
        problem = Problem.objects.get(id=1)
        field_label = problem._meta.get_field('description')
        self.assertEquals(field_label, 'what up?')

    def test_problem_type(self):
        problem = Problem.objects.get(id=1)
        field_label = problem._meta.get_field('slug')
        self.assertEquals(field_label, 'AB')

    def test_problem_type_max_length(self):
        problem = Problem.objects.get(id=1)
        max_length = problem._meta.get_field('slug').max_length
        self.assertEquals(max_length, 255)

class JudgeSpecTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        JudgeSpec.create(type='Batch', mem_limit_bytes= 1024, time_limit_seconds = 2, grader = "https://hello.hello.hello", test_data="https://bye.bye.bye")

    def test_judge_spec_label(self):
        verbose = JudgeSpec._meta.verbose_name.title()
        self.assertEquals(verbose, '채점기준')

    def test_judge_spec_plural_label(self):
        verbose = JudgeSpec._meta.verbose_name_plural.title()
        self.assertEquals(verbose, '채점기준')

    def test_judge_spec_type(self):
        judge_spec= JudgeSpec.objects.get(id=1)
        field_label = judge_spec._meta.get_field('type')
        self.assertEquals(field_label, 'Batch')

    def test_judge_spec_mem_limit_bytes(self):
        judge_spec= JudgeSpec.objects.get(id=1)
        field_label = judge_spec._meta.get_field('mem_limit_bytes')
        self.assertEquals(field_label, 1024)

    def test_judge_spec_time_limit_seconds(self):
        judge_spec= JudgeSpec.objects.get(id=1)
        field_label = judge_spec._meta.get_field('time_limit_seconds')
        self.assertEquals(field_label, 2)

    def test_judge_spec_type_max_length(self):
        judge_spec = JudgeSpec.objects.get(id=1)
        max_length = judge_spec._meta.get_field('type').max_length
        self.assertEquals(max_length, 255)

    def test_judge_spec_grader(self):
        judge_spec = JudgeSpec.objects.get(id=1)
        field_label = judge_spec._meta.get_field('grader')
        self.assertEquals(field_label, "https://hello.hello.hello")

    def test_judge_spec_test_data(self):
        judge_spec = JudgeSpec.objects.get(id=1)
        field_label = judge_spec._meta.get_field('test_data')
        self.assertEquals(field_label, "https://bye.bye.bye")

class TagTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Tag.create(name = 'Dynamic Programming', description = 'trade off')

    def test_tag_label(self):
        verbose = Tag._meta.verbose_name.title()
        self.assertEquals(verbose, '태그')

    def test_tag_plural_label(self):
        verbose = Tag._meta.verbose_name_plural.title()
        self.assertEquals(verbose, '태그')

    def test_tag_name(self):
        tag = Tag.objects.get(id=1)
        field_label = tag._meta.get_field('name')
        self.assertEquals(field_label, 'Dynamic Programming')

    def test_tag_name_max_length(self):
        tag = Tag.objects.get(id=1)
        max_length = tag._meta.get_field('name').max_length
        self.assertEquals(max_length, 255)

    def test_tag_description(self):
        tag = Tag.objects.get(id=1)
        field_label = tag._meta.get_field('description')
        self.assertEquals(field_label, 'trade off')

class SubmissionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Submission.create(lang_profile='c++', submission_data="https://submission.data.url")

    def test_submission_verbose(self):
        verbose = Submission._meta.verbose_name.title()
        self.assertEquals(verbose, '제출')

    def test_submission_plural_verbose(self):
        verbose = Submission._meta.verbose_name_plural.title()
        self.assertEquals(verbose, '제출')

    def test_submission_lang_profile(self):
        submission = submission.objects.get(id=1)
        field_label = submission._meta.get_field('lang_profile')
        self.assertEquals(field_label, 'c++')

    def test_submission_data(self):
        submission = submission.objects.get(id=1)
        field_label = submission._meta.get_field('submission_data')
        self.assertEquals(field_label, 'https://submission.data.url')

class JudgeResult(TestCase):
    @classmethod
    def setUpTestData(cls):
        JudgeResult.create(status='PASS', memory_used_bytes=123, time_elapsed_seconds=1.2, code_size=255, score=100)

    def test_judge_result_verbose(self):
        verbose = JudgeResult._meta.verbose_name.title()
        self.assertEquals(verbose, '채점결과')

    def test_judge_result_plural_verbose(self):
        verbose = JudgeResult._meta.verbose_name_plural.title()
        self.assertEquals(verbose, '채점결과')

    def test_judget_result_status(self):
        result = JudgeResult.objects.get(id=1)
        field_label = result._meta.get_field('status')
        self.assertEquals(field_label, 'PASS')

    def test_judget_result_status_max_length(self):
        result = JudgeResult.objects.get(id=1)
        max_length = result._meta.get_field('status').max_length
        self.assertEquals(max_length, 255)

    def test_judge_result_memory_used_bytes(self):
        result = JudgeResult.objects.get(id=1)
        field_label = result._meta.get_field('memory_used_bytes')
        self.assertEquals(field_label, 123)

    def test_judge_result_time_elapsed_seconds(self):
        result = JudgeResult.objects.get(id=1)
        field_label = result._meta.get_field('time_elapsed_seconds')
        self.assertEquals(field_label, 1.2)

    def test_judge_result_code_size(self):
        result = JudgeResult.objects.get(id=1)
        field_label = result._meta.get_field('code_size')
        self.assertEquals(field_label, 255)

    def test_judge_result_score(self):
        result = JudgeResult.objects.get(id=1)
        field_label = result._meta.get_field('score')
        self.assertEquals(field_label, 100)
