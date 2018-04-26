import api.models as models

from django.contrib import admin


admin.site.register(models.Gym)
admin.site.register(models.GymProblem)
admin.site.register(models.Problem)
admin.site.register(models.ProblemTag)
admin.site.register(models.Tag)
admin.site.register(models.JudgeSpec)
admin.site.register(models.Submission)
admin.site.register(models.JudgeResult)
