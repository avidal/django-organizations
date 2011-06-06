# django-organizations

This project aims to provide a solution for projects that require more flexible
user accounts. Each user is tied to one or more organizations and is a member
of one or more roles per organization. Usernames must be unique within a given
organization, and the login process adds a field for the name of the organization.

## Organizations

An organization is the top-level collection of members. Every user has
a primary organization, and an optional list of secondary organizations.

## Users

## Scratch

orgusers must be a member of a primary organization which is used for various
purposes.

orgusers can optionally be a member of multiple other organizations.

orgusers can take on any role that is provided by any organization they are
a member of.

there are two types of roles, SuperRoles and Roles. A super role is a role that
grants the given permissions on any organization. A regular role is attached to
a specific organization.

an orguser that needs a specific permission regardless of the organization
should take on a super role.
