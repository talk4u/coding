from django.urls import path

from rest_framework_extensions.routers import ExtendedSimpleRouter
from rest_framework_swagger.views import get_swagger_view

import api.views as views

router = ExtendedSimpleRouter()

router.register(r'users', views.UserViewSet, base_name='user')

router.register(r'gyms', views.GymViewSet, base_name='gym')\
      .register(r'problems',
                views.ProblemViewSet,
                base_name='gyms-problem',
                parents_query_lookups=['gym'])

problems_router = router.register(r'problems', views.ProblemViewSet, base_name='problem')
problems_router.register(r'tags',
                         views.TagViewSet,
                         base_name='problems-tag',
                         parents_query_lookups=['problem'])
problems_router.register(r'submissions',
                         views.SubmissionViewSet,
                         base_name='problems-submission',
                         parents_query_lookups=['problem'])

schema_view = get_swagger_view(title='Coding API')

urlpatterns = [
    path(r'docs/', schema_view),
]

urlpatterns += router.urls
