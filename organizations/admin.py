from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User, Group

from .models import Organization, OrganizationUser, SuperRole, Role


class OrganizationUserCreationForm(UserCreationForm):

    username = forms.RegexField(label='Username', max_length=70,
                                regex=r'^[\w.@+-]+$',
                                help_text='Required. 70 characters or fewer.')

    class Meta:
        model = OrganizationUser
        fields = ("organization", "username")


class OrganizationUserChangeForm(UserChangeForm):

    username = forms.RegexField(label='Username', max_length=70,
                                regex=r'^[\w.@+-]+$',
                                help_text='Required. 70 characters or fewer.')

    def __init__(self, *args, **kwargs):
        super(OrganizationUserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('roles', None)
        if f is not None:
            qs = f.queryset
            orgs = list(self.instance.organizations.all())
            orgs.append(self.instance.organization)

            qs = qs.filter(organization__in=orgs)
            f.queryset = qs

    class Meta:
        model = OrganizationUser


class OrganizationUserAdmin(UserAdmin):
    add_form = OrganizationUserCreationForm

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('organization', 'username', 'password1', 'password2')},
        ),
    )

    form = OrganizationUserChangeForm

    fieldsets = (
        (None, {'fields': ('organization', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Additional organizations', {'fields': ('organizations',)}),
        ('Roles', {'fields': ('super_roles', 'roles')}),
    )

    list_display = ('username', 'organization', 'first_name', 'last_name',
                    'is_staff')
    list_filter = ('organization', 'is_staff', 'is_superuser', 'is_active')


admin.site.register(OrganizationUser, OrganizationUserAdmin)
admin.site.register(Organization)
admin.site.register(SuperRole)
admin.site.register(Role)

# Unregister the default django admins for user and groups
admin.site.unregister(User)
admin.site.unregister(Group)
