from django.urls import path
from rest_framework_extensions.routers import ExtendedSimpleRouter
from rest_framework_jwt.views import obtain_jwt_token

import api.views as views

router = ExtendedSimpleRouter()

router.register(r'users', views.UserViewSet, base_name='user')

router.register(r'gyms', views.GymViewSet, base_name='gym')

problems_router = router.register(r'problems', views.ProblemViewSet, base_name='problem')
problems_router.register(r'tags',
                         views.TagViewSet,
                         base_name='problems-tag',
                         parents_query_lookups=['problem'])
problems_router.register(r'submissions',
                         views.SubmissionViewSet,
                         base_name='problems-submission',
                         parents_query_lookups=['problem'])

urlpatterns = [
    path('api-token-auth/', obtain_jwt_token),
]

urlpatterns += router.urls
