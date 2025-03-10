import os
from pprint import pprint

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()
from app_permission.serializers import CustomUserSelectSerializer, GroupWithUsersSelectSerializer
from app_system.models import CustomUser
from django.contrib.auth.models import Group


if __name__ == "__main__":
    lst = [1, 2, 3]
    print(lst)

    lst2 = [*lst, 4]
    print(lst2)




