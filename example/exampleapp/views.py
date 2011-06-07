from django.http import HttpResponse

from organizations.models import OrganizationUser


def list_roles(request):
    """Lists all roles for all users."""

    users = OrganizationUser.objects.order_by('username').all()

    out = []

    # build a dictionary for each user that lists their super roles and
    # organization roles
    for user in users:
        superroles = []
        organizations = []

        out.append("<h1>User: {0}</h1>".format(user))

        for role in user.super_roles.all():
            superroles.append('<li>{0}</li>'.format(role.name))

        out.append('<h2>Super Roles</h2>')
        out.append('<ul>{0}</ul>'.format("\n".join(superroles)))

        for org in user.get_all_organizations():
            roles = []
            for role in user.roles.filter(organization=org):
                roles.append('<li>{0}</li>'.format(role.name))

            organizations.append('<h3>{0}</h3>'.format(org.name))
            organizations.append('<ul>{0}</ul>'.format("\n".join(roles)))

        out.append('<h2>Organizations</h2>')
        out.append("\n".join(organizations))

    return HttpResponse(out)
