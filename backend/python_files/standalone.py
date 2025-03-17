import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

if __name__ == "__main__":
    print(int(float('77.03')))
