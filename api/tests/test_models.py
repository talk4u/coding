from django.test import TestCase

# Create your tests here.

from api.models import User, Gym, GymProblem, JudgeResult, JudgeSpec, Problem, Submission, Tag


class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(self):
        # Set up non-modified objects used by all test methods
        self.user=User.objects.create(first_name='승용1', last_name='이1')

    def test_first_name_label(self):
        user = self.user
        field_label = user._meta.get_field('first_name').verbose_name
        self.assertEquals(field_label, '이름')

    def test_last_name_label(self):
        user = self.user
        field_label = user._meta.get_field('last_name').verbose_name
        self.assertEquals(field_label, '성')

    def test_first_name_max_length(self):
        user = self.user
        max_length = user._meta.get_field('first_name').max_length
        self.assertEquals(max_length, 30)

    def test_object_name_is_last_name_space_first_name(self):
        user = self.user
        expected_object_name = '%s %s' % (user.last_name, user.first_name)
        self.assertEquals(expected_object_name, str(user))

    def test_get_name(self):
        user = self.user
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
        self.assertEquals(gym.name, '도장 1')

    def test_gym_name_max_length(self):
        gym= Gym.objects.get(id=1)
        max_length = gym._meta.get_field('name').max_length
        self.assertEquals(max_length, 255)

    def test_gym_description(self):
        gym= Gym.objects.get(id=1)
        self.assertEquals(gym.description, 'activated for test')

    def test_gym_description_max_length(self):
        gym= Gym.objects.get(id=1)
        max_length = gym._meta.get_field('description').max_length
        self.assertEquals(max_length, 255)

    def test_gym_slug(self):
        gym = Gym.objects.get(id=1)
        self.assertEquals(gym.slug, 'A')

    def test_gym_description_max_length(self):
        gym= Gym.objects.get(id=1)
        max_length = gym._meta.get_field('slug').max_length
        self.assertEquals(max_length, 255)


class ProblemTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.prob=Problem.objects.create(type='problem type 0', name='problem 0', description='what up?', slug='AB' )

    def test_problem_label(self):
        verbose = Problem._meta.verbose_name.title()
        self.assertEquals(verbose, '문제')

    def test_problem_plural_label(self):
        verbose = Problem._meta.verbose_name_plural.title()
        self.assertEquals(verbose, '문제')

    def test_problem_type(self):
        # problem = Problem.objects.get(id=1)
        self.assertEquals(self.prob.type, 'problem type 0')

    def test_problem_type_max_length(self):
        problem = self.prob
        max_length = problem._meta.get_field('type').max_length
        self.assertEquals(max_length, 255)

    def test_problem_name(self):
        problem = self.prob
        self.assertEquals(self.prob.name, 'problem 0')

    def test_problem_type_max_length(self):
        problem = self.prob
        max_length = problem._meta.get_field('name').max_length
        self.assertEquals(max_length, 255)

    def test_problem_description(self):
        problem = self.prob
        self.assertEquals(self.prob.description, 'what up?')

    def test_problem_type(self):
        problem = self.prob
        self.assertEquals(self.prob.slug, 'AB')

    def test_problem_type_max_length(self):
        problem = self.prob
        max_length = problem._meta.get_field('slug').max_length
        self.assertEquals(max_length, 255)


class GymProblemTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        gym=Gym.objects.create(name= '도장 1', description= 'activated for test', slug= 'A')
        prob = Problem.objects.create(type='problem type 1', name='problem 1', description='what up?', slug='AB' )
        gymprob = GymProblem.objects.create(gym=gym, problem=prob, order =1, is_active=True)

    def test_gym_prob_order(self):
        gymprob = GymProblem.objects.get(id=1)
        self.assertEquals(gymprob.order, 1)

    def test_gym_prob_isactive(self):
        gymprob = GymProblem.objects.get(id=1)
        self.assertEquals(gymprob.is_active, True)



class JudgeSpecTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        prob= Problem.objects.create(type='problem type 1', name='problem 1', description='what up?', slug='AB' )
        JudgeSpec.objects.create(problem= prob, type='Batch', mem_limit_bytes= 1024, time_limit_seconds = 2, grader = "https://hello.hello.hello", test_data="https://bye.bye.bye")

    def test_judge_spec_label(self):
        verbose = JudgeSpec._meta.verbose_name.title()
        self.assertEquals(verbose, '채점기준')

    def test_judge_spec_plural_label(self):
        verbose = JudgeSpec._meta.verbose_name_plural.title()
        self.assertEquals(verbose, '채점기준')

    def test_judge_spec_type(self):
        judge_spec= JudgeSpec.objects.get(id=1)
        self.assertEquals(judge_spec.type, 'Batch')

    def test_judge_spec_mem_limit_bytes(self):
        judge_spec= JudgeSpec.objects.get(id=1)
        self.assertEquals(judge_spec.mem_limit_bytes, 1024)

    def test_judge_spec_time_limit_seconds(self):
        judge_spec= JudgeSpec.objects.get(id=1)
        self.assertEquals(judge_spec.time_limit_seconds, 2)

    def test_judge_spec_type_max_length(self):
        judge_spec = JudgeSpec.objects.get(id=1)
        max_length = judge_spec._meta.get_field('type').max_length
        self.assertEquals(max_length, 255)

    def test_judge_spec_grader(self):
        judge_spec = JudgeSpec.objects.get(id=1)
        self.assertEquals(judge_spec.grader, "https://hello.hello.hello")

    def test_judge_spec_test_data(self):
        judge_spec = JudgeSpec.objects.get(id=1)
        self.assertEquals(judge_spec.test_data, "https://bye.bye.bye")

class TagTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Tag.objects.create(name = 'Dynamic Programming', description = 'trade off')

    def test_tag_label(self):
        verbose = Tag._meta.verbose_name.title()
        self.assertEquals(verbose, '태그')

    def test_tag_plural_label(self):
        verbose = Tag._meta.verbose_name_plural.title()
        self.assertEquals(verbose, '태그')

    def test_tag_name(self):
        tag = Tag.objects.get(id=1)
        self.assertEquals(tag.name, 'Dynamic Programming')

    def test_tag_name_max_length(self):
        tag = Tag.objects.get(id=1)
        max_length = tag._meta.get_field('name').max_length
        self.assertEquals(max_length, 255)

    def test_tag_description(self):
        tag = Tag.objects.get(id=1)
        self.assertEquals(tag.description, 'trade off')

class SubmissionTest(TestCase):
    @classmethod
    def setUpTestData(self):
        user=User.objects.create(first_name='승용', last_name='이')
        prob=Problem.objects.create(type='problem type 1', name='problem 1', description='what up?', slug='AB' )
        self.sub=Submission.objects.create(user=user, problem=prob, lang_profile='c++', submission_data="https://submission.data.url")

    def test_submission_verbose(self):
        verbose = Submission._meta.verbose_name.title()
        self.assertEquals(verbose, '제출')

    def test_submission_plural_verbose(self):
        verbose = Submission._meta.verbose_name_plural.title()
        self.assertEquals(verbose, '제출')

    def test_submission_lang_profile(self):
        submission = self.sub
        self.assertEquals(submission.lang_profile, 'c++')

    def test_submission_data(self):
        submission = self.sub
        self.assertEquals(submission.submission_data, 'https://submission.data.url')

class JudgeResultTest(TestCase):
    @classmethod
    def setUpTestData(self):
        json = {
            "item 1" : "hi",
            "bluh" : "blah"
        }
        user=User.objects.create(first_name='승용', last_name='이')
        prob=Problem.objects.create(type='problem type 1', name='problem 1', description='what up?', slug='AB' )
        sub=Submission.objects.create(user=user, problem=prob, lang_profile='c++', submission_data="https://submission.data.url")
        self.result=JudgeResult.objects.create(submission=sub,status='PASS', memory_used_bytes=123, time_elapsed_seconds=2, code_size=255, score=100, detail = json)

    def test_judge_result_verbose(self):
        verbose = JudgeResult._meta.verbose_name.title()
        self.assertEquals(verbose, '채점결과')

    def test_judge_result_plural_verbose(self):
        verbose = JudgeResult._meta.verbose_name_plural.title()
        self.assertEquals(verbose, '채점결과')

    def test_judget_result_status(self):
        result = self.result
        self.assertEquals(result.status, 'PASS')

    def test_judget_result_status_max_length(self):
        result = self.result
        max_length = result._meta.get_field('status').max_length
        self.assertEquals(max_length, 255)

    def test_judge_result_memory_used_bytes(self):
        result = self.result
        self.assertEquals(result.memory_used_bytes, 123)

    def test_judge_result_time_elapsed_seconds(self):
        result = self.result
        self.assertEquals(result.time_elapsed_seconds, 2)

    def test_judge_result_code_size(self):
        result = self.result
        self.assertEquals(result.code_size, 255)

    def test_judge_result_score(self):
        result = self.result
        self.assertEquals(result.score, 100)
