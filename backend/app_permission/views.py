from copy import deepcopy

from django.contrib.auth.models import Group, Permission
from django.db import transaction
from django.db.models import Q, Prefetch
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_permission.models import ModuleConfiguration, CustomPermission, DynamicForm, DynamicFormRecord
from app_permission.permissions import ModuleWiseGroupPermissions
from app_permission.serializers import ModuleConfigSerializer, GroupWithUsersSelectSerializer, CustomUserSelectSerializer, \
    ModuleConfigurationSerializer
from app_system.models import CustomUser
from python_files.techno_generic import TechnoPermissionMixin, TechnoGenericAPIView, ClientException


class SideBarView(TechnoPermissionMixin, APIView):
    model = ModuleConfiguration
    queryset = ModuleConfiguration.objects.filter(is_del=False).select_related(
        'react_box_icon'
    ).prefetch_related(
        'permissions', 'permissions__content_type', 'children'
    ).order_by('sequence')
    modules = ['sidebar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recur_check = 100
        self.all_modules = []

    def get(self, request, *args, **kwargs):
        data = self.get_modules_data()
        all_modules = self.all_modules
        is_permission_manager = request.user.has_model_perms(Group, 'change')
        return Response(data={
            'data': data,
            'all_modules': all_modules,
            'is_permission_manager': is_permission_manager,
        }, status=status.HTTP_200_OK)

    def get_modules_data(self):
        def get_recur_modules(menus, path=()):
            if self.recur_check <= 0:
                raise Exception('Allowed Recur Length Exceeded for Module Configuration')
            self.recur_check -= 1
            lst = []
            for menu in menus:
                if menu.menu_type == 'dropdown':
                    children = get_recur_modules(menus=menu.children.all().order_by('sequence'), path=[*path, menu.codename])
                    if children:
                        self.all_modules.append({
                            'codename': menu.codename,
                            'name': menu.name,
                            'path': [*path, menu.codename],
                        })
                        lst.append({
                            'id': menu.codename,
                            'label': menu.name,
                            'link': menu.page_url,
                            'icon': menu.react_box_icon.class_name if menu.react_box_icon else '',
                            'subItems': children,
                        })

                elif menu.menu_type == 'navigation' or menu.menu_type == 'route':
                    perms = menu.permissions.all()
                    if perms.exists():
                        has_perm = any([
                            self.request.user.has_perm(f'{perm.content_type.app_label}.{perm.codename}')
                            for perm in perms
                        ])
                    else:
                        has_perm = True
                    if has_perm:
                        self.all_modules.append({
                            'codename': menu.codename,
                            'link': menu.page_url,
                            'name': menu.name,
                            'dynamic_form': menu.dynamic_form.id if menu.dynamic_form else '',
                            'path': [*path, menu.codename],
                        })
                        children = get_recur_modules(menus=menu.children.order_by('sequence'), path=[*path, menu.codename])
                        if menu.menu_type == 'navigation':
                            dic = {
                                'id': menu.codename,
                                'label': menu.name,
                                'link': menu.page_url,
                                'icon': menu.react_box_icon.class_name if menu.react_box_icon else '',
                            }
                            if children:
                                dic['children'] = children
                            lst.append(dic)
            return lst

        main_menus = self.queryset.filter(Q(is_root_menu=True) | Q(is_global_menu=True)).order_by('sequence')
        return get_recur_modules(main_menus)


class ModuleWiseGroupPermissionView(TechnoGenericAPIView):
    permission_classes = [IsAuthenticated, ModuleWiseGroupPermissions]
    model = ModuleConfiguration
    serializer_class = ModuleConfigSerializer
    modules = ['module_wise_group_permission']

    def get_queryset(self):
        """ Sending Data in Recursive Tree Structure """
        return self.model.objects.prefetch_related('children').filter(
            Q(is_root_menu=True) | Q(is_global_menu=True)
        ).order_by('sequence')

    @staticmethod
    def get_human_readable_permission_name(perm):
        """ Change default 'Can add user' to 'Add User' for better readability """
        if perm.name.startswith('Can '):
            return perm.name.removeprefix('Can ').title()
        return perm.name

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if self.has_action('get_permissions_by_codename'):
            try:
                record = ModuleConfiguration.objects.prefetch_related(
                    'permissions', 'permissions__content_type', 'custom_permissions').get(
                    codename=self.get_request_data().get('codename'))
            except Exception:
                raise ClientException(f'{self.title} Not Found')

            all_perms = record.permissions.all()
            custom_permissions = CustomPermission.objects.filter(Q(modules=record) | Q(perm_scope='Global'))

            is_perm_exists = all_perms.exists()
            is_custom_perm_exists = custom_permissions.exists()

            all_groups = Group.objects.prefetch_related('user_set')
            if is_perm_exists:
                all_groups = all_groups.prefetch_related(
                    Prefetch(lookup='permissions', queryset=all_perms),
                    'permissions__content_type',
                )
            if is_custom_perm_exists:
                all_groups = all_groups.prefetch_related(
                    Prefetch(lookup='custom_permissions', queryset=custom_permissions)
                )

            permission_mapping = dict()
            if is_perm_exists:
                # Display model wise accordion in FE
                content_type_set = {perm.content_type for perm in all_perms}

                for content_type in content_type_set:

                    # Sample card for model permissions
                    model_perms = [perm for perm in all_perms if perm.content_type == content_type]
                    sample_card = [{
                        'permission_id': perm.pk,
                        'name': self.get_human_readable_permission_name(perm),
                        'has_perm': False
                    } for perm in model_perms]

                    cards = []
                    for group in all_groups:
                        # Filter groups that have any permission for this model
                        group_permissions = group.permissions.values_list('pk', flat=True)
                        if any(perm.pk in group_permissions for perm in model_perms):
                            cards.append({
                                'rec_id': group.pk,
                                'name': group.name,
                                'permissions': [{
                                    'permission_id': perm.pk,
                                    'name': self.get_human_readable_permission_name(perm),
                                    'has_perm': perm.pk in group_permissions
                                } for perm in model_perms],
                            })

                    permission_mapping[content_type.pk] = {
                        'title': content_type.name.capitalize(),
                        'cards': cards,
                        'sample_card': sample_card
                    }

            if is_custom_perm_exists:
                # Display custom accordion for "Custom Permission" in FE

                # Sample card for custom permissions
                sample_card = [{
                    'custom_permission_id': perm.pk,
                    'name': perm.name,
                    'has_perm': False
                } for perm in custom_permissions]

                cards = []
                for group in all_groups:
                    # Filter groups that have any custom permission
                    group_permissions = group.custom_permissions.values_list('pk', flat=True)
                    if any(perm.pk in group_permissions for perm in custom_permissions):
                        cards.append({
                            'rec_id': group.pk,
                            'name': group.name,
                            'permissions': [{
                                'custom_permission_id': perm.pk,
                                'name': perm.name,
                                'has_perm': perm.pk in group_permissions
                            } for perm in custom_permissions],
                        })

                permission_mapping['custom_permissions'] = {
                    'title': 'Custom Permissions',
                    'cards': cards,
                    'sample_card': sample_card
                }

            all_users = CustomUser.objects.all()
            response.data.update({
                'permission_mapping': permission_mapping,
                'all_groups': all_groups,
                'all_users': all_users,
            })

            all_groups = Group.objects.prefetch_related(
                Prefetch('user_set', queryset=CustomUser.objects.filter(is_del=False))
            )
            all_users = CustomUser.objects.filter(is_del=False)
            response.data.update({
                'all_groups': GroupWithUsersSelectSerializer(all_groups, many=True).data,
                'all_users': CustomUserSelectSerializer(all_users, many=True).data,
            })

        return response

    def put(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                for dic in request.data['data']:
                    group_obj = Group.objects.get(pk=dic.get('rec_id'))
                    for perm_dic in dic.get('permissions', []):
                        if 'permission_id' in perm_dic:
                            perm_obj = Permission.objects.get(pk=perm_dic.get('permission_id'))
                            has_perm = perm_dic.get('has_perm')
                            if has_perm is True:
                                group_obj.permissions.add(perm_obj)
                            elif has_perm is False:
                                group_obj.permissions.remove(perm_obj)
                        elif 'custom_permission_id' in perm_dic:
                            perm_obj = CustomPermission.objects.get(pk=perm_dic.get('custom_permission_id'))
                            has_perm = perm_dic.get('has_perm')
                            if has_perm is True:
                                group_obj.custom_permissions.add(perm_obj)
                            elif has_perm is False:
                                group_obj.custom_permissions.remove(perm_obj)
                return Response({'Success': 'Permission Saved Successfully'}, status=status.HTTP_200_OK)
        except:
            transaction.rollback()
            raise


class ModuleConfigurationView(TechnoGenericAPIView):
    model = ModuleConfiguration
    serializer_class = ModuleConfigurationSerializer
    modules = ['module_configuration']


class DynamicModuleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        rec_id = self.kwargs.get('rec_id')
        dynamic_form = DynamicForm.objects.get(pk=rec_id)

        response = dict()
        can_view = self.request.user.has_dynamic_perms(dynamic_form, "View")
        can_add = self.request.user.has_dynamic_perms(dynamic_form, "Add")
        can_change = self.request.user.has_dynamic_perms(dynamic_form, "Change")
        can_delete = self.request.user.has_dynamic_perms(dynamic_form, "Delete")
        can_view = can_view or can_change or can_delete

        get_data = self.has_action("get_data")
        fetch_record = self.has_action("fetch_record")

        is_form = self.has_param("is_form")
        get_perms = self.has_param("get_perms")
        get_form_configs = self.has_param("get_form_configs")
        get_title = self.has_param("get_title")
        get_fields = self.has_param("get_fields") or True

        if get_perms:
            response["permissions"] = {
                '__add': can_add,
                '__change': can_change,
                '__view': can_view,
                '__delete': can_delete,
            }

        if get_title:
            response["title"] = dynamic_form.name

        if get_form_configs:
            response["form_configs"] = (
                self.get_form_configs(dynamic_form) if (can_add or can_change) else dict()
            )

        if get_fields:
            response['fields'] = {row.codename: row.name for row in dynamic_form.fields.all()}

        if get_data:
            response["data"] = [{**row.record, 'rec_id': row.pk} for row in dynamic_form.records.all()] if can_view else []

        elif fetch_record:
            rec_id = self.get_request_data().get("rec_id")
            record = DynamicFormRecord.objects.get(pk=rec_id, dynamic_form=dynamic_form)
            if is_form:
                response["data"] = {**record.record, 'rec_id': record.pk} if (can_add or can_change) else dict()
            else:
                response["data"] = {**record.record, 'rec_id': record.pk} if (can_add or can_change) else dict()

        return Response(response, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        dynamic_form = DynamicForm.objects.get(pk=self.kwargs.get('rec_id'))
        record = DynamicFormRecord.objects.create(record=self.get_request_data(), dynamic_form=dynamic_form)
        return Response(
            data={'data': {**record.record, 'rec_id': record.pk}, 'message': f"{dynamic_form.name} Created Successfully"},
            status=status.HTTP_201_CREATED
        )

    def put(self, request, *args, **kwargs):
        dynamic_form = DynamicForm.objects.get(pk=self.kwargs.get('rec_id'))
        record = DynamicFormRecord.objects.get(pk=self.get_request_data().pop('rec_id'), dynamic_form=dynamic_form)
        record.record = self.get_request_data()
        record.save()
        return Response(
            data={'data': {**record.record, 'rec_id': record.pk}, 'message': f"{dynamic_form.name} Updated Successfully"},
            status=status.HTTP_200_OK
        )

    def delete(self, request, *args, **kwargs):
        dynamic_form = DynamicForm.objects.get(pk=self.kwargs.get('rec_id'))
        ids = self.get_request_data().getlist('ids[]', [])
        records = DynamicFormRecord.objects.filter(pk__in=ids)
        for record in records:
            record.is_del = True
            record.save()
        return Response(
            data={'delete_confirmation': True, 'ids': ids, 'message': f"{dynamic_form.name} Deleted Successfully"},
            status=status.HTTP_200_OK
        )

    def get_request_data(self):
        if self.request.method in ["GET", "DELETE"]:
            return self.request.GET
        if self.request.method in ["PUT", "POST"]:
            return self.request.data
        raise Exception("Invalid Request")

    @staticmethod
    def get_form_configs(dynamic_form):
        configs = dict()
        default_values = dict()
        for field in dynamic_form.fields.all():
            field_name = field.name
            key = field.codename
            field_type = field.field_type
            validation = field.validation or dict()

            configs[key] = dict(type=field_type, name=field_name)
            # configs[key]['validators'] = "Frontend Pending"
            if field_type == "select":
                configs[key]["options"] = validation.get('choices')
            default_values[key] = validation.get('default', None)
        return {
            "fields": configs,
            "defaultValues": default_values,
        }

    def has_param(self, key):
        return self.get_request_data().get(key, "False").lower() == "true"

    def has_action(self, key):
        return self.get_request_data().get("action", None) == key
