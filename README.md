**This project is dead for the time being and is nowhere near ready to be used in production.**

# django-organizations

This project aims to provide a solution for projects that require more flexible
user accounts. Each user is tied to one or more organizations and is a member
of one or more roles per organization. Usernames must be unique within a given
organization, and the login process adds a field for the name of the organization.

## Warning

This application performs some changes to the User model, as well as to the
admin. There's no guarantee that it will work with any other applications you
may be using. It was developed for an internal project at my office where we
needed this support and it's working well for us in production.

## Installation

Installation is simple. Install the application via whichever package manager
you prefer, add a few entries to `INSTALLED_APPS`, and sync your database.
South migrations are provided, and South usage is recommended.

Install via pip:

```
$ pip install django-annoying
```

Add `organizations.patch` and `organizations` to `INSTALLED_APPS`:

```
# settings.py

INSTALLED_APPS = (
    'organizations.patch',
    'django.contrib.admin',
    # ...
    'organizations'
)
```

*Note*: `organizations.patch` MUST come before `django.contrib.admin` to patch
properly.

Add the organizations authentication backend:

```
# settings.py

AUTHENTICATION_BACKENDS = (
    'organizations.backends.OrganizationBackend',
)
```

*Note*: To function properly, `OrganizationBackend` MUST come before the
regular django auth ModelBackend. For most purposes, the regular ModelBackend
is not required.

Sync your database:

```
# if not using South:
$ manage.py syncdb

# if using South:
$ manage.py migrate
```

If you do not use South, you must manually alter the default auth user table to
remove the unique constraint on the username and change the username length to
80 characters.

## Organizations

An organization is the top-level collection of members. Every user has
a primary organization, and an optional list of secondary organizations.

## Users

This application provides a new user model, named `OrganizationUser`. This
model is a subclass of the auth `User` model, so it inherits all of the
properties of the regular `User` model.

Each OrganizationUser must be a member of at least one organization. They can
also be added to multiple additional organizations. These organizations
determine which `Roles` the user can be a part of.

## Roles

A `Role` is similar to an auth `Group`, with one notable exception: it is
attached to a given `Organization.` An `OrganizationUser` can be a member of
any role that is provided by any of the organizations they are a part of.

## Super Roles

A `SuperRole` is similar to a regular `Role`, but it is not tied to a specific
`Organization`. Any permission that is inherited via a `SuperRole` membership
is implicitly available for every organization. These roles are useful for
administrative work.

## Admin Patching

There is a sub-application named `organizations.patch` that performs some basic
patches to make the admin easier to use with this application. Notably, it
connects to the `class_prepared` signal to modify the `User` model to remove
the unique constraint on the username as well as to expand the length of the
username to 80 characters instead of 30.

The other patch that it performs is a patch of the login form for the admin, to
add the organization field to the form. The updated template is provided in
`organizations/patch/templates/admin/login.html`

## Authentication Backend

The authentication backend supports object permissions. There must be an
attribute on each model that you want to support that is a FK to an
`Organization` object. The default attribute name is `organization`, but it can
be overridden with the `_ORGANIZATION_ATTRIBUTE` attribute on the model class:

```python
from django.db import models
from organizations.models import Organization


class MyModel(models.Model):
    org = models.ForeignKey(Organization)
    _ORGANIZATION_ATTRIBUTE = 'org'
```

User permissions are not supported. Instead, the user should be in a super role
or a regular role for any given permission.

The role-based permission checks go in phases:

* If the user is a superuser, return every permission
* If the user is in a SuperRole which grants a given permission, they have
  access.
* If the supplied object is an Organization, then it is equivalent to below,
  where they have that permission if they are a member of the organization
  supplied, and they are in a Role that provides that permission through that
  organization.
* If the user is in the organization that the object is attached to, and they
  are in a role for that organization that provides that permission, they have
  access.
