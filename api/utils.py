import api.models as models


def is_student(user):
    return user.groups.filter(name='student').exists()


def is_instructor(user):
    return user.groups.filter(name='instructor').exists()


def is_solver(problem, user):
    return models.JudgeResult.objects.filter(
        status=models.JudgeStatus.PASSED.value,
        score=100,
        submission__user=user
    ).exists()
