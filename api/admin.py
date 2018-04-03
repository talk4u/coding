import api.models as models

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, \
    ReadOnlyPasswordHashField
from django.utils.translation import ugettext_lazy as _


class CustomUserChangeForm(UserChangeForm):
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see this "
            "user's password, but you can change the password using "
            "<a href=\"../password\">this form</a>."
        ),
    )

    class Meta:
        model = get_user_model()
        fields = '__all__'


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = '__all__'


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm


admin.site.register(models.CustomUser, CustomUserAdmin)
admin.site.register(models.Team)
admin.site.register(models.Notice)
admin.site.register(models.Palestra)
admin.site.register(models.PalestraProblem)
admin.site.register(models.Notification)
admin.site.register(models.Problem)
admin.site.register(models.ProblemTag)
admin.site.register(models.Tag)
admin.site.register(models.RecommendedProblem)
admin.site.register(models.DataSet)
admin.site.register(models.Submission)
admin.site.register(models.SubmissionResult)
admin.site.register(models.Channel)
admin.site.register(models.Thread)
