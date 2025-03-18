import os
from collections import defaultdict

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

if __name__ == "__main__":
    d = defaultdict(list)

    print(d['a'])
