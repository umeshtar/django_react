from rest_framework.response import Response
from rest_framework.views import APIView

from app_system.models import MenuItem


# Create your views here.
class IndexView(APIView):
    model = MenuItem

    def get(self, request, *args, **kwargs):

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

        menus = self.model.objects.all()
        main_menus = menus.filter(is_main_menu=True)

        lst = []
        for menu in main_menus:
            print(menu)
        return Response({'data': 'test'})

    def print_menu(self):
        def recur(menus, level=0):
            if menus.exists():
                for menu in menus.all():
                    print(' ' * level, '- ', menu)
                    recur(menus=menu.children, level=level+1)
        recur(menus=self.model.objects.filter(is_main_menu=True))






