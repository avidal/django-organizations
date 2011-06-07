from django.db import models

from ..models import Organization


class TestModelDefaultAttribute(models.Model):

    organization = models.ForeignKey(Organization)


class TestModelCustomAttribute(models.Model):

    org = models.ForeignKey(Organization)

    _ORGANIZATION_ATTRIBUTE = 'org'


class TestModelInvalidCustomAttribute(models.Model):

    _org = models.ForeignKey(Organization)

    _ORGANIZATION_ATTRIBUTE = 'org'


class TestModelNoAttribute(models.Model):
    pass


class TestModelInvalidFK(models.Model):

    organization = models.CharField(max_length=100)
