from django.db.models.signals import class_prepared


def patch_user(sender, *args, **kwargs):

    authmodels = 'django.contrib.auth.models'
    if sender.__name__ == 'User' and sender.__module__ == authmodels:

        # patch the length
        sender._meta.get_field('username').max_length = 80

        # patch the help text
        help_text = "Required. 80 characters or fewer."
        sender._meta.get_field('username').help_text = help_text

        # remove the unique constraint
        sender._meta.get_field('username').unique = False


class_prepared.connect(patch_user)

# Monkey patch the default admin login form with our custom form
def patch_admin_login():
    from django import forms
    from django.contrib import admin
    from django.contrib import auth

    ERROR_MESSAGE = "Please enter a correct organization, username, and password."

    def patched_clean(self):
        organization = self.cleaned_data.get('organization')
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        message = ERROR_MESSAGE

        if all([organization, username, password]):
            self.user_cache = auth.authenticate(organization=organization,
                                                username=username,
                                                password=password)
            if not self.user_cache:
                raise forms.ValidationError(message)
            if not self.user_cache.is_active or not self.user_cache.is_staff:
                raise forms.ValidationError(message)

        self.check_for_test_cookie()
        return self.cleaned_data

    org_field = forms.CharField(max_length=80)

    admin.forms.AdminAuthenticationForm.base_fields['organization'] = org_field
    admin.forms.AdminAuthenticationForm.clean = patched_clean

patch_admin_login()
