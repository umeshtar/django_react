from rest_framework.views import APIView

from .models import ModuleConfiguration


# Create your views here.
class IndexView(APIView):
    pass


def get_modules_data(user):
    def get_recur_modules(modules):
        lst = []
        for module in modules:
            if module.module_type == 'drop-down':
                children = get_recur_modules(module.children.exclude(pk=module.pk))
                if children:
                    lst.append({
                        'name': module.name,
                        'type': module.module_type,
                        'page_url': module.page_url,
                        'icon': module.react_box_icon.class_name if module.react_box_icon else '',
                        'children': children,
                    })

            elif module.module_type == 'navigation':
                has_perm = any([
                    user.has_perm(f'{perm.content_type.app_label}.{perm.codename}')
                    for perm in module.permissions.all()
                ])
                if has_perm:
                    dic = {
                        'name': module.name,
                        'type': module.module_type,
                        'page_url': module.page_url,
                        'icon': module.react_box_icon.class_name if module.react_box_icon else '',
                    }
                    children = get_recur_modules(module.children.exclude(pk=module.pk))
                    if children:
                        dic['children'] = children
                    lst.append(dic)
        return lst

    main_modules = ModuleConfiguration.objects.filter(
        is_root_menu=True).prefetch_related('permissions', 'permissions__content_type', 'children')
    return get_recur_modules(main_modules)
