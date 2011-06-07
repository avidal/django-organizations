from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission

from .models import Organization, OrganizationUser


class OrganizationBackend(ModelBackend):

    supports_object_permissions = True

    def authenticate(self, organization=None, username=None, password=None):

        if organization is None:
            return None

        try:
            organization = Organization.objects.get(code__iexact=organization)
        except Organization.DoesNotExist:
            return None

        try:
            user = OrganizationUser.objects.get(organization=organization,
                                                username__iexact=username,
                                                user__is_active=True)
            if user.check_password(password):
                return user

        except OrganizationUser.DoesNotExist:
            return None

    def _create_permission_set(self, perms=None):
        """
        Expects a queryset of permissions, returns a formatted
        set.
        """

        if perms is None:
            return set()

        if isinstance(perms, (list, tuple)):
            perms = [(perm.content_type.app_label, perm.codename)
                     for perm in perms]

        else:
            perms = perms.values_list('content_type__app_label',
                                        'codename').order_by()

        return set(['%s.%s' % (ct, name) for ct, name in perms])


    def get_group_permissions(self, user_obj, obj=None):
        """
        Returns a set of all permission strings that this user has through
        his/her roles for the given object.

        We use the `group` designator just for consistency.
        """

        # superusers get all permissions, like usual
        if user_obj.is_superuser:
            perms = Permission.objects.all()
            return self._create_permission_set(perms)

        # if the user is not an OrganizationUser, return the empty set
        if not isinstance(user_obj, OrganizationUser):
            return set()

        # if the user is not in any roles, return the empty set
        super_role_count = user_obj.super_roles.count()
        if not any([super_role_count, user_obj.roles.count()]):
            return set()

        # first, get the perms provided by the super roles
        perms = Permission.objects.filter(superrole__organizationuser=user_obj)

        # now, check the regular role permissions if they are in the
        # organization that owns the object
        attname = getattr(obj, '_ORGANIZATION_ATTRIBUTE', 'organization')
        obj_org = getattr(obj, attname, None)

        if obj_org is None:
            # If the object doesn't have an organization, they can't get
            # any role-based permissions
            pass
        elif obj_org not in user_obj.get_all_organizations():
            # If the user is not in the organization that owns the object,
            # they can't get any role-based permissions
            pass
        else:
            # Otherwise, the user is in the organization that owns the
            # object, so check role permissions
            roles = user_obj.roles.all()
            role_perms = Permission.objects.filter(role__in=roles)
            perms = perms | role_perms

        return self._create_permission_set(perms)

    def get_all_permissions(self, user_obj, obj=None):
        if user_obj.is_anonymous():
            return set()

        # we don't support user permissions
        return self.get_group_permissions(user_obj, obj=obj)

    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_active:
            return False

        return perm in self.get_all_permissions(user_obj, obj=obj)

    def has_module_perms(self, user_obj, app_label, obj=None):
        if not user_obj.is_active:
            return False

        for perm in self.get_all_permissions(user_obj, obj=obj):
            if perm[:perm.index('.')] == app_label:
                return True

        return False

    def get_user(self, user_id):
        try:
            return OrganizationUser.objects.get(pk=user_id)
        except OrganizationUser.DoesNotExist:
            return None
