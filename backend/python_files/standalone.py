import os
from pprint import pprint

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from app_system.models import MenuItem

if __name__ == '__main__':
    sample = [
        {
            'name': 'Employee',
            'type': 'navigation',
            'perm': True,
            'children': [
                {
                    'name': 'Employee Bank',
                    'type': 'navigation',
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
                },
                {
                    'name': 'City',
                    'type': 'navigation',
                    'perm': True,
                },
                {
                    'name': 'State',
                    'type': 'navigation',
                    'perm': True,
                },
                {
                    'name': 'Country',
                    'type': 'navigation',
                    'perm': True,
                },
            ]
        },
        {
            'name': 'Company',
            'type': 'navigation',
            'perm': True,
        },
        {
            'name': 'Company Branch',
            'type': 'navigation',
            'perm': True,
        },
        {
            'name': 'System Configuration',
            'type': 'navigation',
            'perm': True,
        },
    ]

    user = User.objects.get(pk=1)
    all_menus = MenuItem.objects.prefetch_related('permissions').all()
    main_menus = all_menus.filter(is_main_menu=True)

    def recur(menus):
        lst = []
        for menu in menus:
            if menu.menu_type == 'drop-down':
                children = recur(menu.children.all())
                if children:
                    lst.append({
                        'name': menu.name,
                        'type': menu.menu_type,
                        'children': children,
                    })
            else:
                has_perm = False
                for perm in menu.permissions.all():
                    has_perm = user.has_perm(perm)
                    if has_perm:
                        break
                print(menu, has_perm)
                if has_perm:
                    dic = {
                        'name': menu.name,
                        'type': menu.menu_type,
                    }
                    children = recur(menu.children.all())
                    if children:
                        dic['children'] = children
                    lst.append(dic)
        return lst
    pprint(recur(main_menus))

