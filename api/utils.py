import api.models as models


def is_student(user):
    return user.groups.filter(name='student').exists()


def is_instructor(user):
    return user.groups.filter(name='instructor').exists()


def is_solver(problem, user):
    return models.JudgeResult.objects.filter(
        status=models.JudgeStatus.passed.value,
        score=100,
        submission__user=user
    ).exists()


def update_dict_in_exist_keys(dict1, dict2):
    for key, value in dict1.items():
        if key in dict2:
            dict1[key] = dict2[key]
    return dict1
