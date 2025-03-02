from django.contrib.auth.models import Group
from rest_framework.permissions import BasePermission


class ModuleWiseGroupPermissions(BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method == 'PUT':
            return request.user.has_model_perms(Group, 'change')

        return True




