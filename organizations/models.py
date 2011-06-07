import datetime

from django.contrib.auth.models import User, Permission
from django.db import models
from django.utils.translation import ugettext_lazy as _


__all__ = ('Organization', 'SuperRole', 'Role', 'OrganizationUser')

_EMPTY = object()


class Organization(models.Model):
    """
    An organization is a top-level entity that describes a given organization.
    The code is the primary key and is used for login purposes.
    """
    code = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=80)

    def __unicode__(self):
        return self.name


class SuperRole(models.Model):

    name = models.CharField(_('name'), max_length=80, unique=True)
    permissions = models.ManyToManyField(Permission, blank=True)

    def __unicode__(self):
        return self.name


class Role(models.Model):

    name = models.CharField(_('name'), max_length=80)
    organization = models.ForeignKey(Organization)
    permissions = models.ManyToManyField(Permission, blank=True)

    def __unicode__(self):
        return '{0} {1}'.format(self.organization, self.name)

    class Meta:
        unique_together = [('name', 'organization')]


class OrganizationUserManager(models.Manager):

    def create_user(self, organization, username, email, password=None):
        now = datetime.datetime.now()

        # Normalize the address by lowercasing the domain part of the email
        # address.
        try:
            email_name, domain_part = email.strip().split('@', 1)
        except ValueError:
            pass
        else:
            email = '@'.join([email_name, domain_part.lower()])

        user = self.model(organization=organization, username=username,
                          email=email, is_staff=False, is_active=True,
                          is_superuser=False, last_login=now,
                          date_joined=now)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, organization, username, email, password):
        u = self.create_user(organization, username, email, password)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u

    def make_random_password(self, length=10, allowed_chars=_EMPTY):
        """
        Generates a random password with the given length and given allowed_chars
        """

        if allowed_chars is _EMPTY:
            allowed_chars = 'abcdefghjkmnpqrstuvwxyz'
            allowed_chars += allowed_chars.upper()
            allowed_chars += '23456789'

        # Note that default value of allowed_chars does not have "I" or letters
        # that look like it -- just to avoid confusion.
        from random import choice
        return ''.join([choice(allowed_chars) for i in range(length)])


class OrganizationUser(User):

    user = models.OneToOneField(User, related_name='orguser', parent_link=True)

    organization = models.ForeignKey(Organization,
                                     related_name='primary_members')
    organizations = models.ManyToManyField(Organization, blank=True,
                                           related_name='members')

    super_roles = models.ManyToManyField(SuperRole, blank=True)
    roles = models.ManyToManyField(Role, blank=True)

    objects = OrganizationUserManager()

    @property
    def full_name(self):
        fn = '{0} {1}'.format(self.first_name, self.last_name)
        return fn.strip()

    @property
    def display_name(self):
        return '{0} - {1}'.format(self.username, self.full_name)

    def __unicode__(self):
        fmt = '{0} @ {1}'
        if self.full_name:
            return fmt.format(self.full_name, self.organization)
        else:
            return fmt.format(self.username, self.organization)
