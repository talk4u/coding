import api.models as models

from django.contrib import admin


class GymProblemInline(admin.TabularInline):
    model = models.GymProblem
    extra = 2  # how many rows to show


class GymUserInline(admin.TabularInline):
    model = models.GymUser
    extra = 2  # how many rows to show


class GymAdmin(admin.ModelAdmin):
    inlines = (GymProblemInline, GymUserInline)


class ProblemTagInline(admin.TabularInline):
    model = models.ProblemTag
    extra = 2


class ProblemAdmin(admin.ModelAdmin):
    inlines = (ProblemTagInline,)


admin.site.register(models.Gym, GymAdmin)
admin.site.register(models.Problem, ProblemAdmin)
admin.site.register(models.Tag)
admin.site.register(models.JudgeSpec)
admin.site.register(models.Submission)
admin.site.register(models.JudgeResult)
