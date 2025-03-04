import os
from pprint import pprint

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()
from app_permission.serializers import CustomUserSelectSerializer, GroupWithUsersSelectSerializer
from app_system.models import CustomUser
from django.contrib.auth.models import Group


if __name__ == "__main__":
    s = CustomUserSelectSerializer(CustomUser.objects.all(), many=True)
    pprint(s.data)

    s = GroupWithUsersSelectSerializer(Group.objects.all(), many=True)
    pprint(s.data)
