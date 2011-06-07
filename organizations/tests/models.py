from django.test import TestCase

from ..models import Organization, OrganizationUser


class OrganizationUserModelTest(TestCase):

    def setUp(self):
        # create a list of organizations
        for i in range(5):
            code = 'testorg%d' % i
            name = 'Org %d' % i
            Organization.objects.create(code=code, name=name)

        self.orgs = Organization.objects.order_by('pk').all()

    def test_organization_list(self):
        "Users should have the correct list of organizations"

        org = self.orgs[0]

        user = OrganizationUser.objects.create_user(organization=org,
                                                    username='testuser',
                                                    email='test@test.com')

        get_orgs = lambda: user.get_all_organizations().order_by('pk')

        self.assertEqual(get_orgs().count(), 1)
        self.assertQuerysetEqual(get_orgs(), map(repr, [org]))

        # add another organization to the user
        org2 = self.orgs[1]
        user.organizations.add(org2)

        self.assertEqual(get_orgs().count(), 2)
        self.assertQuerysetEqual(get_orgs(), map(repr, [org, org2]))


class OrganizationModelTest(TestCase):

    def setUp(self):
        # create a list of users and one organization
        self.org = Organization.objects.create(code='testorg', name='TestOrg')
        self.org2 = Organization.objects.create(code='testorg2',
                                                name='TestOrg2')

        for i in range(5):
            OrganizationUser.objects.create_user(organization=self.org,
                                                 username='testuser%d' % i,
                                                 email='test%d@test.com' % i)

        self.users = OrganizationUser.objects.all()

    def test_membership(self):

        self.assertQuerysetEqual(self.users.order_by('username'),
            map(repr, self.org.primary_members.order_by('username')))

        # move some users from primary to secondary membership
        for i in (0,1):
            u = self.users[i]
            u.organization = self.org2
            u.organizations.add(self.org)
            u.save()

        self.assertQuerysetEqual(self.org.primary_members.all(),
                                 map(repr, self.users[2:]))

        self.assertQuerysetEqual(self.org.members.all(),
                                 map(repr, self.users[:2]))

        self.assertQuerysetEqual(self.org.all_members().all(),
                                 map(repr, self.users))
