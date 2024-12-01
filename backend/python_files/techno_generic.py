import inspect
import json
import os
import traceback
from collections import defaultdict

from django.core.exceptions import ImproperlyConfigured
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Q, ProtectedError
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import ChoiceField
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.relations import PrimaryKeyRelatedField, ManyRelatedField
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import exception_handler

from app_system.models import ModuleConfiguration, CustomPermission


def encrypt_id(rec_id):
    return str(int(rec_id) + 270000981)


def decrypt_id(rec_id):
    return int(rec_id) - 270000981


def get_field_verbose_name(model, field_name):
    return model._meta.get_field(field_name).verbose_name.capitalize()


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


def has_model_perm(user, model, perm='any'):
    app_label = model._meta.app_label
    model_name = model._meta.model_name
    perm_code = f"{app_label}.{{perm}}_{model_name}"

    if perm == 'any':
        return any([
            user.has_perm(perm_code.format(perm='view')),
            user.has_perm(perm_code.format(perm='add')),
            user.has_perm(perm_code.format(perm='change')),
            user.has_perm(perm_code.format(perm='delete')),
        ])

    if perm == 'all':
        return all([
            user.has_perm(perm_code.format(perm='view')),
            user.has_perm(perm_code.format(perm='add')),
            user.has_perm(perm_code.format(perm='change')),
            user.has_perm(perm_code.format(perm='delete')),
        ])

    return user.has_perm(perm_code.format(perm=perm))


def techno_representation(instance, data, is_form, serializer):
    data['rec_id'] = encrypt_id(instance.pk)
    for k, v in serializer.get_fields().items():
        if isinstance(v, ChoiceField):
            if is_form is False:
                value = getattr(instance, k, None)
                if value:
                    data[k] = v.choices[value]
        elif isinstance(v, PrimaryKeyRelatedField):
            inst = getattr(instance, k, None)
            if inst:
                data[k] = encrypt_id(inst.pk) if is_form else str(inst)
        elif isinstance(v, ManyRelatedField):
            qs = getattr(instance, k, None)
            if qs and qs.exists():
                data[k] = [encrypt_id(inst.pk) if is_form else str(inst) for inst in qs.all()]
    return data


def decrypt_post_data(data, serializer_class=None, fks=(), m2m=()):
    fks = list(fks)
    m2m = list(m2m)
    if serializer_class:
        for k, v in serializer_class().get_fields().items():
            if isinstance(v, PrimaryKeyRelatedField):
                fks.append(k)
            if isinstance(v, ManyRelatedField):
                m2m.append(k)
    for k in fks:
        if k in data and data[k]:
            data[k] = decrypt_id(data[k])

    for k in m2m:
        if k in data and data[k]:
            data[k] = [decrypt_id(value) for value in data[k] if value]
    return data


def custom_exception_handler(exc, context):
    if isinstance(exc, ValidationError):
        form_errors = dict()
        for k, v in exc.detail.items():
            if isinstance(v, list):
                form_errors[k] = ', '.join(v)
            elif isinstance(v, str):
                form_errors[k] = v
        return Response({'form_errors': form_errors}, status=exc.status_code)

    if isinstance(exc, ProtectedError):
        return Response({'message': 'Can not delete due to protected records'}, status=status.HTTP_400_BAD_REQUEST)

    if isinstance(exc, ClientException):
        return Response({'message': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    response = exception_handler(exc, context)
    if response is not None:
        return response

    file_path = 'error_log.txt'
    with open(file_path, 'a' if os.path.exists(file_path) else 'w') as file:
        file.write(f'Timestamp: {timezone.now()}\n')
        file.write(f'Error Traceback: {traceback.format_exc()}\n\n')
    return Response({'message': 'Something Went Wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClientException(Exception):
    pass


class ReactHookForm:
    __field_types = {
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
    __recur_field_list = ['add_by', 'modify_by', 'delete_by', 'is_del', 'add_date', 'modify_date', 'delete_date']

    def __init__(self, serializer):
        self.__serializer = serializer()
        self.__select_options_func = dict()
        self.__verbose_name = dict()

    def set_select_options_func(self, **kwargs):
        self.__select_options_func.update(kwargs)
        return self

    def set_verbose_name(self, **kwargs):
        self.__verbose_name.update(kwargs)
        return self

    def get_configs(self, fields=(), exclude=(), ignore_recur_fields=True):
        configs = dict()
        default_values = dict()
        serializer_fields = self.__serializer.get_fields()
        if ignore_recur_fields is True:
            serializer_fields = {k: v for k, v in serializer_fields.items() if k not in self.__recur_field_list}
        if fields:
            serializer_fields = {k: v for k, v in serializer_fields.items() if k in fields}
        if exclude:
            serializer_fields = {k: v for k, v in serializer_fields.items() if k not in exclude}
        for key, field in serializer_fields.items():
            if key in self.__verbose_name:
                field_name = self.__verbose_name[key]
            else:
                field_name = get_field_verbose_name(model=self.__serializer.Meta.model, field_name=key)
            configs[key] = dict()
            configs[key]['type'] = field_type = self.__get_field_type(field)
            configs[key]['name'] = field_name
            configs[key]['rules'] = self.__get_rules(field, field_type, field_name)
            if field_type == 'select':
                configs[key]['options'] = self.__get_options(key, field)
            default_values[key] = self.__get_default_values(field)
        return {
            'fields': configs,
            'defaultValues': default_values,
        }

    @staticmethod
    def __get_default_values(field):
        return field.initial if field.initial is not None else ''

    def __get_field_type(self, field):
        if field.style and 'base_template' in field.style and field.style['base_template'] == 'textarea.html':
            return 'textarea'
        return self.__field_types[field.__class__.__name__]

    @staticmethod
    def __get_rules(field, field_type, field_name):
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

    def __get_options(self, key, field):
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
                dic = {'value': encrypt_id(inst.pk), 'label': str(inst)}
                if key in self.__select_options_func:
                    dic.update(**self.__select_options_func[key](inst))
                if type(inst).__name__ == 'Tbl_Country_Code':
                    dic['code'] = inst.country_code.replace('+', '')
                data.append(dic)
            return data

        if choices:
            return [{'value': value, 'label': label} for value, label in choices.items()]

        return []


class TechnoSerializerValidation:
    __error_msg = {
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
        self.__model = model
        self.__instance = instance
        self.__attrs = None
        self.__enc_attrs = dict()
        self.__custom_errors = defaultdict(list)
        self.__country_code = dict()

    def set_attrs(self, attrs):
        self.__attrs = attrs

    def set_country_code(self, **kwargs):
        self.__country_code.update(**kwargs)

    def get_enc_attrs(self):
        enc_attrs = self.__enc_attrs
        self.__enc_attrs = dict()
        return enc_attrs

    def get_custom_errors(self):
        custom_errors = self.__custom_errors
        self.__custom_errors = defaultdict(list)
        return custom_errors

    def __get_verbose_name(self, name):
        return self.__model._meta.get_field(name).verbose_name.capitalize()

    def __add_error(self, field):
        calling_func = inspect.stack()[1].frame.f_code.co_name
        error_msg = self.__error_msg[calling_func].format(field=self.__get_verbose_name(field))
        self.__custom_errors[field].append(error_msg)

    def check_empty(self, *args):
        for field in args:
            value = self.__attrs.get(field, None)
            if not value or (isinstance(value, str) and not value.strip()):
                self.__add_error(field)

    def check_same_value(self, field, field2):
        if not field == field2:
            value1 = self.__attrs.get(field, None)
            value2 = self.__attrs.get(field2, None)
            if value1 and value2 and value1 == value2:
                error_msg = self.__error_msg['check_same_value'].format(
                    field1=self.__get_verbose_name(field), field2=self.__get_verbose_name(field2))
                self.__custom_errors[field].append(error_msg)

    def check_exists(self, *args):
        for field in args:
            value = self.__attrs.get(field, None)
            if value:
                filter_dic = {f'{field}__iexact' if isinstance(value, str) else field: value}
                qs = self.__model.objects.filter(is_del=False, **filter_dic)
                if self.__instance is not None:
                    qs = qs.exclude(pk=self.__instance.pk)
                if qs.exists():
                    self.__add_error(field)

    def check_unique_set(self, *args):
        filter_dic = dict()
        for field in args:
            value = self.__attrs.get(field, None)
            if value:
                filter_dic[f'{field}__iexact' if isinstance(value, str) else field] = value
        qs = self.__model.objects.filter(is_del=False, **filter_dic)
        if self.__instance is not None:
            qs = qs.exclude(pk=self.__instance.pk)
        if qs.exists():
            error_msg = self.__error_msg['check_unique_set'].format(
                field=self.__get_verbose_name(args[0]),
                fields=', '.join([self.__get_verbose_name(arg) for arg in args[1:]])
            )
            self.__custom_errors[args[0]].append(error_msg)

    def check_multi_exists(self, *args):
        pass

    # def check_email(self, *args):
    #     for field in args:
    #         value = self.__attrs.get(field, None)
    #         if value and not check_email(value):
    #             self.__add_error(field)

    # def check_phone(self, *args):
    #     for field in args:
    #         value = self.__attrs.get(field, None)
    #         if value:
    #             if field in self.country_code:
    #                 code = self.__attrs.get(self.country_code[field], None)
    #                 code = code.country_dial_code if code else None
    #             else:
    #                 code = '91'
    #             if code and value and check_valid_number(phone_number=value, country_code=code) is False:
    #                 self.__add_error(field)

    def check_future_datetime(self, *args):
        for field in args:
            value = self.__attrs.get(field, None)
            if value and type(value).__name__ == 'date' and value > timezone.now().date():
                self.__add_error(field)

    def check_past_datetime(self, *args):
        for field in args:
            value = self.__attrs.get(field, None)
            if value and type(value).__name__ == 'date' and value < timezone.now().date():
                self.__add_error(field)


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
        custom_errors = self.tsv.get_custom_errors()
        if custom_errors:
            raise ValidationError(custom_errors)
        return attrs

    def techno_validate(self, attrs: dict):
        pass

    def save(self, **kwargs):
        enc_attrs = self.tsv.get_enc_attrs()
        if enc_attrs:
            kwargs.update(enc_attrs)
        request = self.context.get('request', None)
        if request and request.user and request.user.is_authenticated:
            if self.instance:
                kwargs['modify_by'] = request.user
            else:
                kwargs['add_by'] = request.user
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


# noinspection PyUnresolvedReferences
class TechnoPermissionMixin:
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def get_model_permission(self, model_class=None):
        perms = dict()
        if model_class is None:
            model_class = self.model
        app_label = model_class._meta.app_label
        model_name = model_class._meta.model_name.lower()
        perms['__add'] = self.request.user.has_perm(f'{app_label}.add_{model_name}')
        perms['__change'] = self.request.user.has_perm(f'{app_label}.change_{model_name}')
        perms['__view'] = self.request.user.has_perm(f'{app_label}.view_{model_name}')
        perms['__delete'] = self.request.user.has_perm(f'{app_label}.delete_{model_name}')
        if perms['__change'] or perms['__delete']:
            perms['__view'] = True
        return perms

    def get_extra_modules_permissions(self):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name.lower()
        configs = ModuleConfiguration.objects.prefetch_related(
            'permissions', 'permissions__content_type').filter(
            name__in=self.modules).exclude(
            permissions__content_type__app_label=app_label, permissions__content_type__model=model_name)
        check_repeat = []
        perms = defaultdict(dict)
        for config in configs:
            for perm in config.permissions.all():
                app_model_name = f'{perm.content_type.app_label}.{perm.content_type.model}'
                perm_code = f'{perm.content_type.app_label}.{perm.codename}'
                perm_name = perm.codename.rsplit(f'_{perm.content_type.model}')[0]
                model_name = perm.content_type.model
                if model_name not in perms:
                    check_repeat.append(app_model_name)
                    perms[model_name][perm_name] = self.request.user.has_perm(perm_code)
                else:
                    if app_model_name in check_repeat:
                        perms[model_name][perm_name] = self.request.user.has_perm(perm_code)
                    else:
                        perms[app_model_name][perm_name] = self.request.user.has_perm(perm_code)
        return perms

    def get_custom_permission(self):
        perms = dict()
        q_object = Q(modules__name__in=self.modules) | Q(is_common_for_all=True)
        qs = CustomPermission.objects.filter(is_del=False).filter(q_object)
        if qs.exists():
            if self.request.user.is_superuser:
                perms.update({perm.codename: True for perm in qs})
            else:
                perms.update({perm.codename: False for perm in qs})
                qs = qs.filter(Q(users=self.request.user) | Q(groups__user=self.request.user))
                if qs.exists():
                    perms.update({perm.codename: True for perm in qs})
        return perms


# noinspection PyUnresolvedReferences
class TechnoFetchMixin:

    def has_param(self, key):
        return self.request.GET.get(key, 'False').lower() == 'true'

    def has_action(self, key):
        return self.request.GET.get('action', None) == key

    def get_params_response(self, *args, **kwargs):
        response = dict(title=self.title)

        can_view = has_model_perm(user=self.request.user, model=self.model, perm='view')
        can_create = has_model_perm(user=self.request.user, model=self.model, perm='change')
        can_update = has_model_perm(user=self.request.user, model=self.model, perm='add')

        get_crud = self.has_param('get_crud_configs')
        get_record = self.has_action('fetch_record')
        is_form = self.has_param('is_form')
        if get_crud:
            get_perms, get_fields, form_configs, get_data = True, True, True, True
        else:
            get_perms = self.has_param('get_perms')
            get_fields = self.has_param('get_fields')
            form_configs = self.has_param('get_form_configs')
            get_data = self.has_action('get_data')

        if get_perms:
            response['permissions'] = {
                **self.get_model_permission(),
                **self.get_extra_modules_permissions(),
            }
            custom_perms = self.get_custom_permission()
            if custom_perms:
                response['permissions']['__custom'] = custom_perms

        if get_fields:
            if can_view:
                fields = self.get_list_serializer_class().Meta.fields
                extra_kwargs = getattr(self.get_list_serializer_class().Meta, 'extra_kwargs', dict())
                response['fields'] = {
                    field_name: extra_kwargs[field_name]['label']
                    if field_name in extra_kwargs and 'label' in extra_kwargs[field_name]
                    else get_field_verbose_name(self.model, field_name)
                    for field_name in fields
                }
            else:
                response['fields'] = dict()

        if form_configs:
            response['form_configs'] = self.get_form_configs() if (can_create or can_update) else dict()

        if get_data:
            response['data'] = self.get_list_serializer(
                self.get_queryset(), many=True).data if can_view else []

        elif get_record:
            if is_form:
                response['data'] = self.get_serializer(
                    self.get_object()).data if (can_create or can_update) else dict()
            else:
                response['data'] = self.get_detail_serializer(
                    self.get_object()).data if can_view else dict()
        return response

    def fetch(self, request, *args, **kwargs):
        response = self.get_params_response(request, *args, **kwargs)
        return Response(response, status=status.HTTP_200_OK)


# noinspection PyUnresolvedReferences
class TechnoCreateMixin:

    def create(self, request, *args, **kwargs):
        s = self.get_serializer(data=self.get_post_data())
        s.is_valid(raise_exception=True)
        record = s.save()
        return Response({
            'data': self.get_list_serializer(record).data if has_model_perm(
                user=self.request.user, model=self.model, perm='view') else dict(),
            'message': f"{self.title} Created Successfully",
        }, status=status.HTTP_201_CREATED)


# noinspection PyUnresolvedReferences
class TechnoUpdateMixin:

    def update(self, request, *args, **kwargs):
        s = self.get_serializer(data=self.get_post_data(), instance=self.get_object())
        s.is_valid(raise_exception=True)
        inst = s.save()
        return Response({
            'data': self.get_list_serializer(inst).data if has_model_perm(
                user=request.user, model=self.model, perm='view') else dict(),
            'message': f"{self.title} Updated Successfully"
        }, status=status.HTTP_200_OK)


# noinspection PyUnresolvedReferences
class TechnoDeleteMixin:

    def soft_delete(self, request, *args, **kwargs):
        record = self.get_object()
        ids = [encrypt_id(record.pk)]
        record.delete()
        return Response({
            'message': f'{self.title} Deleted Successfully',
            'ids': ids,
        }, status=status.HTTP_200_OK)


class TechnoGenericBaseAPIView(GenericAPIView):
    model = None
    serializer_class = None
    list_serializer_class = None
    detail_serializer_class = None
    title = None
    modules = ('Under Development', )

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if self.model is None:
            raise ImproperlyConfigured(f"Attribute 'model' can not be None")
        if self.serializer_class is None:
            raise ImproperlyConfigured(f"Attribute 'serializer_class' can not be None")
        if not self.modules:
            raise ImproperlyConfigured(f"Attribute 'modules' can not be empty")
        if self.title is None:
            self.title = self.model._meta.verbose_name.capitalize()

    def get_queryset(self):
        return self.model.objects.filter(is_del=False)

    def get_object_lookup_kwargs(self):
        payload = self.get_request_data()
        return dict(pk=decrypt_id(payload['rec_id']))

    def get_object(self):
        return self.get_queryset().get(**self.get_object_lookup_kwargs())

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['is_form'] = self.request.GET.get('is_form', 'False').lower() == 'true'
        return context

    def get_detail_serializer_class(self):
        return self.detail_serializer_class or self.get_list_serializer_class()

    def get_detail_serializer(self, *args, **kwargs):
        detail_serializer_class = self.get_detail_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return detail_serializer_class(*args, **kwargs)

    def get_list_serializer_class(self):
        return self.list_serializer_class or self.serializer_class

    def get_list_serializer(self, *args, **kwargs):
        list_serializer_class = self.get_list_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return list_serializer_class(*args, **kwargs)

    def get_form_configs(self):
        return ReactHookForm(serializer=self.get_serializer_class()).get_configs()

    def get_request_data(self):
        if self.request.method in ['GET', 'DELETE']:
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

        data = decrypt_post_data(data, serializer_class=self.get_serializer_class())
        return data


class TechnoGenericAPIView(TechnoFetchMixin,
                           TechnoCreateMixin,
                           TechnoUpdateMixin,
                           TechnoDeleteMixin,
                           TechnoPermissionMixin,
                           TechnoGenericBaseAPIView):

    def get(self, request, *args, **kwargs):
        return self.fetch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.soft_delete(request, *args, **kwargs)



