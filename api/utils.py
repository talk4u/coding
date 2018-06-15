from django.db.models import Max

import api.models as models


def is_student(user):
    return user.groups.filter(name='student').exists()


def is_instructor(user):  # pragma: no cover
    return user.groups.filter(name='instructor').exists()


def is_solver(problem, user):  # pragma: no cover
    return get_latest_judge_result_queryset(
        models.JudgeResult.objects.filter(
            status=models.JudgeStatus.PASSED.value,
            score=100,
            submission__user=user,
            submission__problem=problem
        )
    ).exists()


def get_latest_judge_result_queryset(qs):
    latest_dates = qs.values('submission_id').annotate(
        latest_created_at=Max('created_at')
    )
    return qs.filter(created_at__in=latest_dates.values('latest_created_at'))


def update_dict_in_exist_keys(dict1, dict2):  # pragma: no cover
    for key, value in dict1.items():
        if key in dict2:
            dict1[key] = dict2[key]
    return dict1
