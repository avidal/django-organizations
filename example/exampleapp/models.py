import uuid

from django.db import models

from organizations.models import Organization


class ExampleModelA(models.Model):

    organization = models.ForeignKey(Organization)
    uuid = models.CharField(max_length=32, default=lambda: uuid.uuid4().hex)


class ExampleModelB(models.Model):

    org = models.ForeignKey(Organization)
    uuid = models.CharField(max_length=32, default=lambda: uuid.uuid4().hex)


class ExampleModelC(models.Model):

    uuid = models.CharField(max_length=32, default=lambda: uuid.uuid4().hex)
