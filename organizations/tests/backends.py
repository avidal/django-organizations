from django.test import TestCase

from django.contrib.auth.models import Permission

from ..backends import OrganizationBackend
from ..models import Organization, Role, SuperRole, OrganizationUser


class PermissionTestCase(TestCase):
    "Test that permissions are returned properly."

    def permstr(self, perms):
        return self.backend._create_permission_set(perms)

    def setUp(self):
        self.org = Organization.objects.create(code='testorg', name='Test Org')
        self.backend = OrganizationBackend()

    def test_superuser_permissions(self):
        "Superusers get all permissions."

        u = OrganizationUser.objects.create_superuser(organization=self.org,
                                                      username='superuser',
                                                      email='super@super.com',
                                                      password='superuser')

        self.assertTrue(u.is_superuser)

        perms = Permission.objects.all()

        self.assertItemsEqual(self.backend.get_all_permissions(u),
                              self.permstr(perms))

        for perm in self.permstr(perms):
            self.assertTrue(self.backend.has_perm(u, perm))

    def test_superrole_permissions(self):
        "SuperRole permissions should apply regardless of Organization"

        # create the super role
        role = SuperRole.objects.create(name='SuperRole')

        # add a few permissions to it
        perms = list(Permission.objects.all()[0:2])
        for perm in perms:
            role.permissions.add(perm)

        # create the actual user
        u = OrganizationUser.objects.create_user(organization=self.org,
                                                 username='testuser',
                                                 email='test@test.com')

        # add them to the super role
        u.super_roles.add(role)

        # and see if they have those permissions
        for perm in self.permstr(perms):
            self.assertTrue(self.backend.has_perm(u, perm))

        # create an object with an organization NOT equal to the users
        # organization
        org2 = Organization.objects.create(code='testorg2', name='Test Org2')
        class T(object):
            organization = org2

        # see if they still have the permissions
        for perm in self.permstr(perms):
            self.assertTrue(self.backend.has_perm(u, perm, obj=T()))

        # use an object attached to the organization they are in
        class T(object):
            organization = u.organization

        for perm in self.permstr(perms):
            self.assertTrue(self.backend.has_perm(u, perm, obj=T()))

    def test_role_permissions(self):
        "Role permissions should only grant access on same-org objects."

        # create the role
        role = Role.objects.create(name='TestRole', organization=self.org)

        # add a few permissions to it
        perms = list(Permission.objects.all()[0:2])
        for perm in perms:
            role.permissions.add(perm)

        # create the actual user
        u = OrganizationUser.objects.create_user(organization=self.org,
                                                 username='testuser',
                                                 email='test@test.com')

        # add them to the role
        u.roles.add(role)

        # make sure they have all permissions without an object
        for perm in self.permstr(perms):
            self.assertTrue(self.backend.has_perm(u, perm))

        # ensure they have permissions if they are in the same organization
        class T(object):
            organization = self.org

        for perm in self.permstr(perms):
            self.assertTrue(self.backend.has_perm(u, perm, obj=T()))

        # no permission if they aren't in the same organization
        org2 = Organization.objects.create(code='testorg2', name='Test Org2')
        class T(object):
            organization = org2

        for perm in self.permstr(perms):
            self.assertFalse(self.backend.has_perm(u, perm, obj=T()))


    def test_blended_permissions(self):
        "Super and regular role permissions should coexist."

        superrole = SuperRole.objects.create(name='SuperRole')
        role = Role.objects.create(organization=self.org, name='Role')

        # assign the same two permissions to each role
        perms = list(Permission.objects.all()[0:2])
        for perm in perms:
            superrole.permissions.add(perm)
            role.permissions.add(perm)

        # create the actual user
        u = OrganizationUser.objects.create_user(organization=self.org,
                                                 username='testuser',
                                                 email='test@test.com')

        # add them to the roles
        u.super_roles.add(superrole)
        u.roles.add(role)

        # they should have both of these permissions on any object
        org2 = Organization.objects.create(code='testorg2', name='Test Org2')

        class T(object):
            pass
        class T1(object):
            organization = self.org
        class T2(object):
            organization = org2

        for obj in (None, T(), T1(), T2()):
            for perm in self.permstr(perms):
                self.assertTrue(self.backend.has_perm(u, perm, obj=obj))

        # add an additional permission to just the super role
        perm = Permission.objects.all()[4]
        superrole.permissions.add(perm)

        perms.append(perm)

        # ensure they still have full access to all permissions,
        # including the new one
        for obj in (None, T(), T1(), T2()):
            for perm in self.permstr(perms):
                self.assertTrue(self.backend.has_perm(u, perm, obj=obj))

        # add an additional permission to just the regular role
        perm = Permission.objects.all()[5]
        role.permissions.add(perm)
        new_permstr = self.permstr([perm]).pop()

        # ensure they still have full access to all permissions
        for obj in (None, T(), T1(), T2()):
            for perm in self.permstr(perms):
                self.assertTrue(self.backend.has_perm(u, perm, obj=obj))

        # ensure they do not have access to the new permission on other
        # objects
        self.assertFalse(self.backend.has_perm(u, new_permstr, obj=T2()))

        # ensure they have the new perm on the good objects
        for obj in (None, T(), T1()):
            self.assertTrue(self.backend.has_perm(u, new_permstr, obj=obj))

    def test_permissions_without_membership(self):
        "Users with a permission for a different org should not have access"

        role = Role.objects.create(organization=self.org, name='Role')

        # assign a couple of permissions to the role
        perms = list(Permission.objects.all()[0:2])
        for perm in perms:
            role.permissions.add(perm)

        # create the actual user
        u = OrganizationUser.objects.create_user(organization=self.org,
                                                 username='testuser',
                                                 email='test@test.com')

        # add them to the role
        u.roles.add(role)

        org2 = Organization.objects.create(code='testorg2', name='Test Org2')

        class T(object):
            pass
        class T1(object):
            organization = self.org
        class T2(object):
            organization = org2

        # the user should have the two permissions on None, T(), and T1()
        for obj in (None, T(), T1()):
            for perm in self.permstr(perms):
                self.assertTrue(self.backend.has_perm(u, perm, obj=obj))

        # the user should not have the permissions on T2()
        for perm in self.permstr(perms):
            self.assertFalse(self.backend.has_perm(u, perm, obj=T2()))
