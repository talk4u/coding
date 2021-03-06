from django.contrib.auth.models import Group
from django.test import TestCase

# Create your tests here.
from rest_framework.reverse import reverse

from api.models import User, Gym, Problem, ProblemType, GymProblem, GymUser


class GymListViewTest(TestCase):
    def setUp(self):
        # Create two group
        group_student = Group.objects.create(name='student')
        group_instructor = Group.objects.create(name='instructor')

        # Create two users
        student1 = User.objects.create_user(username='student1', password='12345')
        student1.groups.add(group_student)
        student1.save()
        student2 = User.objects.create_user(username='student2', password='12345')
        student2.groups.add(group_student)
        student2.save()

        # Create one instructor
        instructor = User.objects.create_user(username='instructor', password='12345')
        instructor.groups.add(group_instructor)
        instructor.save()

        # Create 5 problems
        problem1 = Problem.objects.create(type=ProblemType.batch, slug='A')
        problem2 = Problem.objects.create(type=ProblemType.batch, slug='B')
        problem3 = Problem.objects.create(type=ProblemType.batch, slug='C')
        problem4 = Problem.objects.create(type=ProblemType.batch, slug='D')
        problem5 = Problem.objects.create(type=ProblemType.batch, slug='E')

        # Create two gyms
        gym1 = Gym.objects.create(
            name='구글 인터뷰 준비',
            description='구글 인터뷰 준비를 위한 문제 모음',
            slug='PREPARE_GOOGLE_INTERVIEW'
        )
        # Create problem as a post-step
        problem_objects_for_gym1 = Problem.objects.filter(slug__in=['A', 'B', 'C'])
        for p in problem_objects_for_gym1:
            GymProblem.objects.create(problem=p, gym=gym1)
        for student in [student1, student2]:
            GymUser.objects.create(user=student, gym=gym1)
        gym1.save()

        gym2 = Gym.objects.create(
            name='알고리즘의 기초',
            description='알고리즘 기초를 다지기 위한 문제 모음',
            slug='ALGORITHM_BASIC'
        )
        # Create problem as a post-step
        problem_objects_for_gym2 = Problem.objects.filter(slug__in=['C', 'D', 'E'])
        for p in problem_objects_for_gym2:
            GymProblem.objects.create(problem=p, gym=gym2)
        for student in [student1]:
            GymUser.objects.create(user=student, gym=gym2)
        gym2.save()

        gym3 = Gym.objects.create(
            name='코딩의 기초',
            description='코딩 기초를 다지기 위한 문제 모음',
            slug='CODING_BASIC'
        )
        # Create problem as a post-step
        problem_objects_for_gym3 = Problem.objects.filter(slug__in=['E'])
        for p in problem_objects_for_gym3:
            GymProblem.objects.create(problem=p, gym=gym3)
        for student in []:
            GymUser.objects.create(user=student, gym=gym3)
        gym3.save()

    def test_only_accessible_gyms_by_logged_in_student(self):
        resp = self.client.get(reverse('gym-list'))

        # Check that we got a response "Unauthorized"
        self.assertEqual(resp.status_code, 401)

        login = self.client.login(username='student1', password='12345')
        resp = self.client.get(reverse('gym-list'))

        # Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        # User1 must get gym1 and gym2
        self.assertEqual(len(resp.json()), 2)

        login = self.client.login(username='student2', password='12345')
        resp = self.client.get(reverse('gym-list'))

        # Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        # User1 must get only gym1
        self.assertEqual(len(resp.json()), 1)

    def test_gyms_by_logged_in_instructor(self):
        resp = self.client.get(reverse('gym-list'))

        # Check that we got a response "Unauthorized"
        self.assertEqual(resp.status_code, 401)

        login = self.client.login(username='instructor', password='12345')
        resp = self.client.get(reverse('gym-list'))

        # Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        # instructor must get gym1 and gym2 and gym3
        self.assertEqual(len(resp.json()), 3)