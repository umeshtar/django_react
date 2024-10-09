import os
from pprint import pprint

import django
from django.apps import apps
from django.urls import get_resolver, resolve, reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from app_system.models import MenuItem


if __name__ == '__main__':
    sample = [
        {
            'name': 'Dashboard',
            'type': 'navigation',
            'perm': True,
        },
        {
            'name': 'Employee',
            'type': 'navigation',
            'perm': False,
            'routes': [
                {
                    'name': 'Bank',
                    'type': 'route',
                    'perm': True,
                }
            ]
        },
        {
            'name': 'Master',
            'type': 'drop-down',
            'perm': None,
            'children': [
                {
                    'name': 'Department',
                    'type': 'navigation',
                    'perm': True,
                }
            ]
        },
    ]

    menus = MenuItem.objects.all()
    main_menus = menus.filter(is_main_menu=True)
    user = User.objects.get(pk=2)

    lst = []
    for menu in main_menus:
        dic = {
            'name': menu.name,
            'type': menu.menu_type,
            'perm': False,
        }
        if menu.menu_type == 'drop-down':
            lst2 = []
            for child in menu.children.all():
                dic2 = {
                    'name': child.name,
                    'type': child.menu_type,
                    'perm': False,
                }
                if child.menu_type == 'navigation':
                    for module in child.modules.all():
                        rev = reverse(module.url_name)
                        res = resolve(rev)
                        model = res.func.view_class.model

                lst2.append(dic2)
            dic['children'] = lst2
        elif menu.menu_type == 'navigation':
            pass
        elif menu.menu_type == 'route':
            pass
        lst.append(dic)
        # print(menu)
        # print(menu.modules.all())

    print('======================')
    pprint(lst)






