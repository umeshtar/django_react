import re

from rest_framework.exceptions import ValidationError


def validate_codename(value):
    if not re.fullmatch(pattern=r"^[a-z]+(?:_[a-z0-9]+)*$", string=value):
        raise ValidationError("Entered Value is not a valid codename")
