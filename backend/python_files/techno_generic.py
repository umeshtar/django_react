
import inspect
import json
from collections import defaultdict

from django.core.exceptions import ImproperlyConfigured
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.fields import ChoiceField
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.relations import PrimaryKeyRelatedField, ManyRelatedField
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt import authentication


class ReactHookForm:
    field_types = {
        'CharField': 'text',
        'URLField': 'url',
        'EmailField': 'email',
        'DateField': 'date',
        'DateTimeField': 'datetime-local',
        'TimeField': 'time',
        'BooleanField': 'checkbox',
        'IntegerField': 'number',
        'FloatField': 'number',
        'DecimalField': 'number',
        'PrimaryKeyRelatedField': 'select',
        'ChoiceField': 'select',
        'ManyRelatedField': 'select',
        'ImageField': 'file',
        'FileField': 'file',
    }
    recur_field_list = ['cipher_text', 'salt', 'nonce', 'tag', 'add_by', 'modify_by',
                        'del_by', 'is_del', 'add_date', 'modify_date', 'del_date', ]

    def __init__(self, serializer):
        self.serializer = serializer()
        self.select_options_func = dict()

    def set_select_options_func(self, **kwargs):
        self.select_options_func.update(kwargs)

    def get_configs(self, fields=(), exclude=(), ignore_recur_fields=True):
        configs = dict()
        default_values = dict()
        serializer_fields = self.serializer.get_fields()
        if ignore_recur_fields is True:
            serializer_fields = {k: v for k, v in serializer_fields.items() if k not in self.recur_field_list}
        if fields:
            serializer_fields = {k: v for k, v in serializer_fields.items() if k in fields}
        if exclude:
            serializer_fields = {k: v for k, v in serializer_fields.items() if k not in exclude}
        for key, field in serializer_fields.items():
            field_name = self.get_field_verbose_name(key)
            configs[key] = dict()
            configs[key]['type'] = field_type = self.get_field_type(field)
            configs[key]['rules'] = self.get_rules(field, field_type, field_name)
            if field_type == 'select':
                configs[key]['options'] = self.get_options(key, field)
            default_values[key] = self.get_default_values(field)
        return {
            'fields': configs,
            'defaultValues': default_values,
        }

    @staticmethod
    def get_default_values(field):
        return field.initial if field.initial is not None else ''

    def get_field_type(self, field):
        if field.style and 'base_template' in field.style and field.style['base_template'] == 'textarea.html':
            return 'textarea'
        return self.field_types[field.__class__.__name__]

    def get_field_verbose_name(self, key):
        return self.serializer.Meta.model._meta.get_field(key).verbose_name.capitalize()

    @staticmethod
    def get_rules(field, field_type, field_name):
        rules = dict()
        if field.required is True and not field_type == 'file':
            rules['required'] = {'value': True, 'message': f"{field_name} is required"}
        if field_type == 'text':
            rules['maxLength'] = {'value': field.max_length,
                                  'message': field.error_messages['max_length'].format(max_length=field.max_length)}
            if field.min_length:
                rules['minLength'] = {'value': field.min_length,
                                      'message': field.error_messages['min_length'].format(min_length=field.min_length)}
        if field_type == 'number':
            if field.min_value:
                rules['min'] = {'value': field.min_value,
                                'message': field.error_messages['min_value'].format(min_value=field.min_value)}
            if field.max_value:
                rules['max'] = {'value': field.max_value,
                                'message': field.error_messages['max_value'].format(max_value=field.max_value)}
        return rules

    def get_options(self, key, field):
        queryset, choices = None, None

        if hasattr(field, 'queryset'):
            queryset = field.queryset.all()

        if hasattr(field, 'choices'):
            choices = field.choices

        if hasattr(field, 'child_relation'):
            if hasattr(field.child_relation, 'queryset'):
                queryset = field.child_relation.queryset.all()

        if queryset and queryset.exists():
            if hasattr(queryset.first(), 'is_del'):
                queryset = queryset.filter(is_del=False)
            data = []
            for inst in queryset:
                dic = {'value': str(inst.pk + 270000981), 'label': str(inst)}
                if key in self.select_options_func:
                    dic.update(**self.select_options_func[key](inst))
                if type(inst).__name__ == 'Tbl_Country_Code':
                    dic['code'] = inst.country_code.replace('+', '')
                data.append(dic)
            return data

        if choices:
            return [{'value': value, 'label': label} for value, label in choices.items()]

        return []


class TechnoSerializerValidation:
    error_msg = {
        'check_empty': '{field} is required',
        'check_exists': '{field} is already exists',
        'check_unique_set': '{field} is already exists with {fields}',
        'check_multi_exists': '{field} is already exists',
        'check_same_value': '{field1} and {field2} can not be same',
        'check_email': '{field} is invalid',
        'check_phone': '{field} is invalid',
        'check_future_datetime': 'Future date(time) is not allowed',
    }

    def __init__(self, model, instance):
        self.model = model
        self.instance = instance
        self.attrs = None
        self.enc_attrs = dict()
        self.custom_errors = defaultdict(list)
        self.non_field_errors = ''
        self.country_code = dict()

    def set_attrs(self, attrs):
        self.attrs = attrs

    def set_country_code(self, **kwargs):
        self.country_code.update(**kwargs)

    def __get_verbose_name(self, name):
        return self.model._meta.get_field(name).verbose_name.capitalize()

    def __add_error(self, field):
        calling_func = inspect.stack()[1].frame.f_code.co_name
        error_msg = self.error_msg[calling_func].format(field=self.__get_verbose_name(field))
        self.custom_errors[field].append(error_msg)

    def check_empty(self, *args):
        for field in args:
            value = self.attrs.get(field, None)
            if not value or (isinstance(value, str) and not value.strip()):
                self.__add_error(field)

    def check_same_value(self, field, field2):
        if not field == field2:
            value1 = self.attrs.get(field, None)
            value2 = self.attrs.get(field2, None)
            if value1 and value2 and value1 == value2:
                error_msg = self.error_msg['check_same_value'].format(
                    field1=self.__get_verbose_name(field), field2=self.__get_verbose_name(field2))
                self.custom_errors[field].append(error_msg)

    def check_exists(self, *args):
        for field in args:
            value = self.attrs.get(field, None)
            if value:
                filter_dic = {f'{field}__iexact' if isinstance(value, str) else field: value}
                qs = self.model.objects.filter(is_del=False, **filter_dic)
                if self.instance is not None:
                    qs = qs.exclude(pk=self.instance.pk)
                if qs.exists():
                    self.__add_error(field)

    def check_unique_set(self, *args):
        filter_dic = dict()
        for field in args:
            value = self.attrs.get(field, None)
            if value:
                filter_dic[f'{field}__iexact' if isinstance(value, str) else field] = value
        qs = self.model.objects.filter(is_del=False, **filter_dic)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            error_msg = self.error_msg['check_unique_set'].format(
                field=self.__get_verbose_name(args[0]),
                fields=', '.join([self.__get_verbose_name(arg) for arg in args[1:]])
            )
            self.custom_errors[args[0]].append(error_msg)

    def check_multi_exists(self, *args):
        pass

    # def check_email(self, *args):
    #     for field in args:
    #         value = self.attrs.get(field, None)
    #         if value and not check_email(value):
    #             self.__add_error(field)

    # def check_phone(self, *args):
    #     for field in args:
    #         value = self.attrs.get(field, None)
    #         if value:
    #             if field in self.country_code:
    #                 code = self.attrs.get(self.country_code[field], None)
    #                 code = code.country_dial_code if code else None
    #             else:
    #                 code = '91'
    #             if code and value and check_valid_number(phone_number=value, country_code=code) is False:
    #                 self.__add_error(field)

    def check_future_datetime(self, *args):
        for field in args:
            value = self.attrs.get(field, None)
            if value and type(value).__name__ == 'date' and value > timezone.now().date():
                self.__add_error(field)

    def check_past_datetime(self, *args):
        for field in args:
            value = self.attrs.get(field, None)
            if value and type(value).__name__ == 'date' and value < timezone.now().date():
                self.__add_error(field)


class TechnoGenericBaseAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [authentication.JWTAuthentication]
    serializer_class = None
    list_serializer_class = None
    title = None
    modules = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = None
        self.modules_data = []
        self.permissions = defaultdict(dict)

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if self.serializer_class is None:
            raise ImproperlyConfigured(f"Attribute 'serializer_class' can not be None")

        self.model = self.serializer_class.Meta.model
        if self.title is None:
            self.title = self.model._meta.verbose_name.capitalize()

        if DjangoModelPermissions not in self.permission_classes:
            raise ImproperlyConfigured(f"Attribute 'permission_classes' missing TechnoModelPermission")
        if not self.modules:
            raise ImproperlyConfigured(f"Attribute 'modules' can not be blank")

        # self.modules_data = self.get_modules_data()
        self.permissions.update(self.get_model_permission())
        # self.permissions.update(self.get_module_permissions())
        # custom_perms = self.get_custom_permission()
        # if custom_perms:
        #     self.permissions['__custom'] = custom_perms

    # def get_modules_data(self):
    #     def get_recur_modules(menus):
    #         lst = []
    #         for menu in menus:
    #             if menu.module_type == 'drop-down':
    #                 children = get_recur_modules(menu.children.exclude(pk=menu.pk))
    #                 if children:
    #                     lst.append({
    #                         'name': menu.name,
    #                         'type': menu.module_type,
    #                         'page_url': menu.page_url,
    #                         'icon': menu.react_box_icon.class_name if menu.react_box_icon else '',
    #                         'children': children,
    #                     })
    #
    #             elif menu.module_type == 'navigation':
    #                 has_perm = any([
    #                     self.request.user.has_perm(f'{perm.content_type.app_label}.{perm.codename}')
    #                     for perm in menu.permissions.all()
    #                 ])
    #                 if has_perm:
    #                     dic = {
    #                         'name': menu.name,
    #                         'type': menu.module_type,
    #                         'page_url': menu.page_url,
    #                         'icon': menu.react_box_icon.class_name if menu.react_box_icon else '',
    #                     }
    #                     children = get_recur_modules(menu.children.exclude(pk=menu.pk))
    #                     if children:
    #                         dic['children'] = children
    #                     lst.append(dic)
    #         return lst
    #
    #     main_menus = ModuleConfiguration.objects.filter(
    #         is_main_menu=True).prefetch_related('permissions__content_type', 'children')
    #     return get_recur_modules(main_menus)

    def get_model_permission(self, model_class=None):
        if not model_class:
            model_class = self.model
        app_label = model_class._meta.app_label
        model_name = model_class._meta.model_name.lower()
        perms = {
            '__add': self.request.user.has_perm(f'{app_label}.add_{model_name}'),
            '__change': self.request.user.has_perm(f'{app_label}.change_{model_name}'),
            '__view': self.request.user.has_perm(f'{app_label}.view_{model_name}'),
            '__delete': self.request.user.has_perm(f'{app_label}.delete_{model_name}'),
        }
        if perms['__change'] or perms['__delete']:
            perms['__view'] = True
        return perms

    # def get_module_permissions(self):
    #     app_label = self.model._meta.app_label
    #     model_name = self.model._meta.model_name.lower()
    #     view_app_model_name = f'{app_label}.{model_name}'
    #
    #     configs = ModuleConfiguration.objects.prefetch_related(
    #         'permissions__content_type').filter(name__in=self.modules)
    #     check_repeat = []
    #     perms = defaultdict(dict)
    #     for config in configs:
    #         for perm in config.permissions.all():
    #             app_model_name = f'{perm.content_type.app_label}.{perm.content_type.model}'
    #             if not app_model_name == view_app_model_name:
    #                 perm_code = f'{perm.content_type.app_label}.{perm.codename}'
    #                 perm_name = perm.codename.rsplit(f'_{perm.content_type.model}')[0]
    #                 model_name = perm.content_type.model
    #                 if model_name not in perms:
    #                     check_repeat.append(app_model_name)
    #                     perms[model_name][perm_name] = self.request.user.has_perm(perm_code)
    #                 else:
    #                     if app_model_name in check_repeat:
    #                         perms[model_name][perm_name] = self.request.user.has_perm(perm_code)
    #                     else:
    #                         perms[app_model_name][perm_name] = self.request.user.has_perm(perm_code)
    #     return perms
    #
    # def get_custom_permission(self):
    #     perms = dict()
    #     q_object = Q(modules__name__in=self.modules) | Q(is_common_for_all=True)
    #     qs = CustomPermission.objects.filter(is_del=False).filter(q_object)
    #     if qs.exists():
    #         if self.request.user.is_superuser:
    #             perms.update({perm.codename: True for perm in qs})
    #         else:
    #             perms.update({perm.codename: perm.is_exempt_perms for perm in qs})
    #             qs = qs.filter(Q(users=self.request.user) | Q(groups__user=self.request.user))
    #             if qs.exists():
    #                 perms.update({perm.codename: True for perm in qs})
    #     return perms

    def get_list_serializer(self, *args, **kwargs):
        if self.list_serializer_class:
            kwargs.setdefault('context', self.get_serializer_context())
            return self.list_serializer_class(*args, **kwargs)
        return self.get_serializer(*args, **kwargs)

    def get_form_configs(self):
        return ReactHookForm(serializer=self.get_serializer_class()).get_configs()

    def get_request_data(self):
        if self.request.method == 'GET':
            return self.request.GET
        if self.request.method in ['PUT', 'POST']:
            return self.request.data
        raise Exception('Invalid Method for def get_request_data(self):')

    def get_post_data(self):
        request_data = self.get_request_data().copy()
        if 'multipart/form-data' in self.request.content_type:
            data = json.loads(request_data.get('data'))
            for k in request_data:
                f = request_data.get(k)
                if type(f) == InMemoryUploadedFile:
                    if f'{k}-clear' in data and data[f'{k}-clear'] is True:
                        data[k] = None
                    else:
                        data[k] = f
        else:
            data = request_data
        serializer_class = self.get_serializer_class()
        for k, v in serializer_class().get_fields().items():
            if k in data and data[k]:
                if isinstance(v, PrimaryKeyRelatedField):
                    if type(data[k]) == dict and 'value' in data[k]:
                        data[k] = int(data[k]['value']) - 270000981
                if isinstance(v, ChoiceField):
                    if type(data[k]) == dict and 'value' in data[k]:
                        data[k] = data[k]['value']
                if isinstance(v, ManyRelatedField):
                    data[k] = [int(row['value']) - 270000981 for row in data[k] if type(row) == dict and 'value' in row]
        return data

    def get_object_lookup_kwargs(self):
        payload = self.get_request_data()
        return dict(
            pk=int(payload['rec_id']) - 270000981,
            salt=payload['salt'],
            nonce=payload['nonce'],
            tag=payload['tag'],
        )

    def get_queryset(self):
        return self.model.objects.filter(is_del=False).order_by('-pk')

    def get_object(self):
        return self.get_queryset().get(**self.get_object_lookup_kwargs())

    def get_serializer_context(self):
        context = super().get_serializer_context()
        action = self.request.GET.get('action', None)
        if action == 'fetch_record' and self.request.GET.get('is_form', 'False').lower() == 'true':
            context['is_form'] = True
        return context

    def fetch_record(self, request, *args, **kwargs):
        """
        Allowed Cases to Call this method
        1. Listing of Data from Queryset, action: get_data
        2. Retrieving Single Object for Displaying Data, action: get_record
        3. Retrieving Single Object for Editing Form, action: fetch_record, is_form: True
        4. Getting Form Configuration for React Hook Form, get_form_configs: True
        4. Getting Permissions for Module, get_perms: True
        """
        response = dict()
        # response['__modules'] = self.get_modules_data()

        get_perms = request.GET.get('get_perms', 'False').lower() == 'true'
        if get_perms:
            response['permissions'] = self.permissions

        get_form_configs = request.GET.get('get_form_configs', 'False').lower() == 'true'
        if get_form_configs:
            if self.permissions['__add'] or self.permissions['__change']:
                response['form_configs'] = self.get_form_configs()
            else:
                response['form_configs'] = dict()

        action = request.GET.get('action', None)
        if action == 'get_data':
            if self.permissions['__view']:
                response['data'] = self.get_list_serializer(self.get_queryset(), many=True).data
            else:
                response['data'] = []

        elif action == 'fetch_record':
            is_form = request.GET.get('is_form', 'False').lower() == 'true'
            if is_form:
                if self.permissions['__change']:
                    response['data'] = self.get_serializer(self.get_object()).data
                else:
                    raise PermissionDenied()
            else:
                if self.permissions['__view']:
                    response['data'] = self.get_list_serializer(self.get_object()).data
                else:
                    raise PermissionDenied()

        return Response(response, status=status.HTTP_200_OK)

    def create_record(self, request, *args, **kwargs):
        return self.create_or_update()

    def update_record(self, request, *args, **kwargs):
        return self.create_or_update(instance=self.get_object())

    def create_or_update(self, instance=None):
        s = self.get_serializer(data=self.get_post_data(), instance=instance)
        s.is_valid(raise_exception=True)
        if instance:
            s.modify_by = self.request.user
        else:
            s.add_by = self.request.user
        inst = s.save()
        data = self.get_list_serializer(inst).data if self.permissions['__view'] else dict()
        msg = f"{self.title} {'Updated' if instance else 'Created'} Successfully"
        status_code = status.HTTP_200_OK if instance else status.HTTP_201_CREATED
        return Response({'data': data, 'Success': msg}, status=status_code)

    def delete_record(self, request, *args, **kwargs):
        pass
        # return delete_records(self.request, model_class=self.model, rec_id_kwargs='rec_id')


class TechnoGenericAPIView(TechnoGenericBaseAPIView):

    def get(self, request, *args, **kwargs):
        return self.fetch_record(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create_record(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update_record(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.delete_record(request, *args, **kwargs)


class TechnoModelSerializer(ModelSerializer):
    class Meta:
        model = None
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.Meta.model or not self.Meta.fields:
            raise ImproperlyConfigured(f'model and/or fields Missing in {self.__class__.__name__} Meta Class')
        self.tsv = TechnoSerializerValidation(model=self.Meta.model, instance=self.instance)

    def validate(self, attrs):
        self.tsv.set_attrs(attrs)
        self.techno_validate(attrs)
        if self.tsv.non_field_errors:
            raise ValidationError(self.tsv.non_field_errors)
        if self.tsv.custom_errors:
            raise ValidationError(self.tsv.custom_errors)
        return attrs

    def techno_validate(self, attrs: dict):
        pass

    def save(self, **kwargs):
        if self.tsv.enc_attrs:
            kwargs.update(self.tsv.enc_attrs)
        return super().save(**kwargs)

    def to_representation(self, instance):
        is_form = self.context.get('is_form', False)
        data = super().to_representation(instance)
        return techno_representation(instance, data, is_form, serializer=self)


class TechnoListSerializer(ModelSerializer):
    class Meta:
        model = None
        fields = []

    def to_representation(self, instance):
        is_form = False
        data = super().to_representation(instance)
        return techno_representation(instance, data, is_form, serializer=self)


def techno_representation(instance, data, is_form, serializer):
    data['rec_id'] = str(instance.pk + 270000981)
    data['salt'] = instance.salt
    data['nonce'] = instance.nonce
    data['tag'] = instance.tag
    for k, v in serializer.get_fields().items():
        if isinstance(v, ChoiceField):
            value = getattr(instance, k, None)
            if value:
                if is_form:
                    data[k] = {'value': value,
                               'label': v.choices[value]}
                else:
                    data[k] = v.choices[value]
        elif isinstance(v, PrimaryKeyRelatedField):
            inst = getattr(instance, k, None)
            if inst:
                if is_form:
                    if hasattr(inst, 'salt'):
                        data[k] = {'value': str(inst.pk + 270000981),
                                   'salt': inst.salt,
                                   'nonce': inst.nonce,
                                   'tag': inst.tag,
                                   'label': str(inst)}
                    else:
                        data[k] = {'value': str(inst.pk + 270000981),
                                   'label': str(inst)}
                else:
                    data[k] = str(inst)
        elif isinstance(v, ManyRelatedField):
            qs = getattr(instance, k, None)
            lst = []
            for inst in qs.all():
                if is_form:
                    if hasattr(inst, 'salt'):
                        value = {
                               'value': str(inst.pk + 270000981),
                               'salt': inst.salt,
                               'nonce': inst.nonce,
                               'tag': inst.tag,
                               'label': str(inst)
                           }
                    else:
                        value = {
                            'value': str(inst.pk + 270000981),
                            'label': str(inst)
                        }
                else:
                    value = str(inst)
                lst.append(value)
            data[k] = lst
    return data


# class ReactBoxIcon(recur_field):
#     name = models.CharField(max_length=100)
#     class_name = models.CharField(max_length=50)
#
#     def __str__(self):
#         return self.name


# class ModuleConfiguration(recur_field):
#     module_type_choices = [
#         ('drop-down', 'drop-down'),
#         ('navigation', 'navigation'),
#         ('route', 'route'),
#     ]
#     name = models.CharField(max_length=100)
#     module_type = models.CharField(max_length=50, choices=module_type_choices)
#     react_box_icon = models.ForeignKey(ReactBoxIcon, on_delete=models.PROTECT, null=True, blank=True)
#     is_main_menu = models.BooleanField(default=False)
#     page_url = models.URLField(null=True, blank=True)
#     permissions = models.ManyToManyField(Permission, blank=True)
#     children = models.ManyToManyField('self', blank=True, symmetrical=False)
#
#     def __str__(self):
#         return self.name
#
#     @staticmethod
#     def allowed_permissions():
#         """ Use in View to Restrict Applying these permissions to users or groups """
#         filter_dic = {
#             'content_type__app_label__startswith': 'App_',
#         }
#         return Permission.objects.filter(**filter_dic).values_list('id', flat=True)


# class CustomPermission(recur_field):
#     element_type_choices = [
#         ('Button', 'Button'),
#     ]
#     name = models.CharField(max_length=200)
#     codename = models.CharField(max_length=100)
#     element_type = models.CharField(max_length=100, choices=element_type_choices, null=True, blank=True)
#     description = models.CharField(max_length=1000)
#     is_common_for_all = models.BooleanField(default=False)
#     is_exempt_perms = models.BooleanField(default=False)
#
#     users = models.ManyToManyField(CustomUser, blank=True, related_name='custom_permissions')
#     groups = models.ManyToManyField(Group, blank=True, related_name='custom_permissions')
#     modules = models.ManyToManyField(ModuleConfiguration, blank=True, related_name='custom_permissions')
#
#     def __str__(self):
#         return self.name


