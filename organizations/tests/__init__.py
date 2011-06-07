# import test models
from .testmodels import TestModelDefaultAttribute, TestModelCustomAttribute, \
        TestModelInvalidCustomAttribute, TestModelNoAttribute, \
        TestModelInvalidFK


# import actual test cases
from .models import OrganizationUserModelTest, OrganizationModelTest
from .backends import PermissionTestCase

# stop pyflakes from freaking out
{
    'testmodels': (TestModelDefaultAttribute, TestModelCustomAttribute,
                   TestModelInvalidCustomAttribute, TestModelNoAttribute,
                   TestModelInvalidFK),
    'models': (OrganizationUserModelTest, OrganizationModelTest),
    'backends': (PermissionTestCase,)
}
