from django.test import TestCase

# Create your tests here.

from api.models import User


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
