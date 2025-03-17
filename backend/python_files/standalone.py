import os
from decimal import Decimal
from pprint import pprint

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()
from app_permission.serializers import CustomUserSelectSerializer, GroupWithUsersSelectSerializer
from app_system.models import CustomUser
from django.contrib.auth.models import Group

if __name__ == "__main__":
    num1 = 10.3
    num2 = 10
    num3 = Decimal('105')

    print(isinstance(num1, int))  # True
    print(isinstance(num2, float))  # True
    print(isinstance(num3, Decimal))  # True

    from decimal import Decimal, ROUND_DOWN


    def validate_decimal(value, decimal_places):
        try:
            return Decimal(value).quantize(Decimal(f"1.{'0' * decimal_places}"), rounding=ROUND_DOWN)
        except:
            return "Invalid decimal"


    print(validate_decimal("12.345", 2))  # 12.34
    print(validate_decimal("10.1", 2))  # 10.10
    print(validate_decimal("5", 2))  # 5.000
    print(validate_decimal("abc", 2))  # Invalid decimal
