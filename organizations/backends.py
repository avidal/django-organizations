from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import check_password

from .models import Organization, OrganizationUser


class OrganizationBackend(ModelBackend):

    def authenticate(self, organization=None, username=None, password=None):
        try:
            organization = Organization.objects.get(code__iexact=organization)
        except Organization.DoesNotExist:
            return None

        try:
            user = OrganizationUser.objects.get(organization=organization,
                                                username__iexact=username,
                                                user__is_active=True)
        except OrganizationUser.DoesNotExist:
            return None

        valid_passwd = check_password(password, user.password)

        return user if valid_passwd else None

    def get_user(self, user_id):
        try:
            return OrganizationUser.objects.get(pk=user_id)
        except OrganizationUser.DoesNotExist:
            return None
