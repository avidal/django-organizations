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

        We accomplish this by pulling the set of all available permissions, then
        checking the object. A superuser immediately gets all of the available
        permissions, and a super role gets all of their super role permissions.

        If an object is not supplied, the returned set contains all permissions
        available to this user. This facilitates things like hiding/showing
        features based on whether or not a user has a permission available.
        """

        # superusers get all permissions, like usual
        if user_obj.is_superuser:
            perms = Permission.objects.all()
            return self._create_permission_set(perms)

        # if the user is not an OrganizationUser, they get no permissions
        if not isinstance(user_obj, OrganizationUser):
            return set()

        # if the user is not in any roles, they get no permissions
        if not any([user_obj.super_roles.count(), user_obj.roles.count()]):
            return set()

        # at this point, they should have some permissions

        # start off with the set of super role permissions
        perms = Permission.objects.filter(superrole__organizationuser=user_obj)

        # next, get the set of permissions provided by the regular roles

        # check the object's organization
        attname = getattr(obj, '_ORGANIZATION_ATTRIBUTE', 'organization')

        # if no object was passed in, or the object doesn't have an
        # organization attribute, include all permissions from all roles
        if obj is None or not hasattr(obj, attname):
            roles = user_obj.roles.all()
            perms = perms | Permission.objects.filter(role__in=roles)

            # done calculating at this point, return early
            return self._create_permission_set(perms)

        # At this point, we know the object is not None and the object
        # has an organization attribute, so fetch the value of the organization
        obj_org = getattr(obj, attname, None)

        # If the value of the organization attribute is None, then return
        # the currently collected permissions
        if obj_org is None:
            return self._create_permission_set(perms)

        # Finally, collect the permissions this user has on this object, based
        # off of the set of organizations they are a member of

        # If the user is not a member of the organization attached to this
        # object, then return the collected permissions
        if obj_org not in user_obj.get_all_organizations():
            return self._create_permission_set(perms)

        # The user is in the organization that owns this object, so collect
        # all of the permissions this user has for this organization
        roles = user_obj.roles.filter(organization=obj_org)
        perms = perms | Permission.objects.filter(role__in=roles)

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
