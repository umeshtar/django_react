import inspect
import json
import os
import traceback
from collections import defaultdict

from django.core.exceptions import ImproperlyConfigured
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import FileExtensionValidator
from django.db.models import Q, ProtectedError
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import ChoiceField, IntegerField, FloatField, DecimalField
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.relations import PrimaryKeyRelatedField, ManyRelatedField
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import exception_handler

from app_system.models import ModuleConfiguration, CustomPermission
from backend.settings import Django_Mode
from python_files.techno_delete import DjangoSoftDelete


def get_field_verbose_name(model, field_name):
    return model._meta.get_field(field_name).verbose_name.capitalize()


def techno_representation(instance, data, is_form, serializer):
    for k, v in serializer.get_fields().items():
        if isinstance(v, ChoiceField):
            if is_form is False:
                value = getattr(instance, k, None)
                if value:
                    data[k] = v.choices[value]
        elif isinstance(v, PrimaryKeyRelatedField):
            inst = getattr(instance, k, None)
            if inst:
                data[k] = inst.pk if is_form else str(inst)
        elif isinstance(v, ManyRelatedField):
            qs = getattr(instance, k, None)
            if qs and qs.exists():
                data[k] = [inst.pk if is_form else str(inst) for inst in qs.all()]
    return data


def custom_exception_handler(exc, context):
    if isinstance(exc, ValidationError):
        form_errors = dict()
        for k, v in exc.detail.items():
            if isinstance(v, list):
                form_errors[k] = ', '.join(v)
            elif isinstance(v, str):
                form_errors[k] = v
        return Response({'form_errors': form_errors}, status=status.HTTP_400_BAD_REQUEST)

    if isinstance(exc, ProtectedError):
        return Response({'message': 'Can not delete due to protected records'}, status=status.HTTP_400_BAD_REQUEST)

    if isinstance(exc, ClientException):
        return Response({'message': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    response = exception_handler(exc, context)
    if response is not None:
        return response

    file_path = 'error_log.txt'
    with open(file_path, 'a' if os.path.exists(file_path) else 'w') as file:
        # Additionally Notify Developer by Task and/or Email as per configuration
        file.write(f'Timestamp: {timezone.now()}\n')
        file.write(f'Error Traceback: {traceback.format_exc()}\n\n')
    return Response({'message': 'Something Went Wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClientException(Exception):
    pass


class ReactHookForm:
    """
        Doc String is Pending
        Manually Specify verbose name for repeaters
        Frontend validator function key mapping is pending
    """
    __stop_mode = False
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

    def __init__(self, serializer, repeater_name=''):
        self.__serializer = serializer()
        self.__select_options_func = dict()
        self.__verbose_name = dict()
        self.__options = dict()
        self.__label = dict()
        self.__repeater_name = repeater_name
        if not Django_Mode == 'Development':
            self.__stop_mode = False

    def set_select_options_func(self, **kwargs):
        self.__select_options_func.update(kwargs)
        return self

    def set_verbose_name(self, **kwargs):
        self.__verbose_name.update(kwargs)
        return self

    def set_options(self, **kwargs):
        self.__options.update(kwargs)
        return self

    def set_label(self, **kwargs):
        self.__label.update(kwargs)
        return self

    def get_configs(self, fields=(), exclude=()):
        configs = dict()
        default_values = dict()
        serializer_fields = self.__serializer.get_fields()
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
            configs[key]['validators'] = self.__get_validators(field, field_type, field_name)
            if field_type == 'select':
                configs[key]['options'] = self.__get_options(key, field)
            default_values[key] = self.__get_default_values(field)
        return {
            'fields': configs,
            'defaultValues': default_values,
        }

    def __get_validators(self, field, field_type, field_name):
        """ Update this function to meet frontend matching keys """
        validators = dict()
        if not field_type == 'file' and hasattr(field, 'required'):
            if isinstance(field, ManyRelatedField):
                validators['required'] = field.allow_empty is False
                validators['checkValid'] = field.allow_empty is True
            else:
                validators['required'] = field.required is True
                validators['checkValid'] = field.required is False

        if field_type == 'text':
            if field.min_length:
                validators['minLength'] = field.min_length
            if field.max_length:
                validators['maxLength'] = field.max_length

        elif field_type == 'email':
            validators['validType'] = 'email'

        elif field_type == 'select':
            if isinstance(field, ManyRelatedField):
                validators['type'] = 'multiple'

        elif field_type == 'url':
            validators['validType'] = 'url'

        elif field_type == 'number':
            if isinstance(field, IntegerField):
                validators['validType'] = 'int'
            elif isinstance(field, FloatField) or isinstance(field, DecimalField):
                validators['validType'] = 'number'

        elif field_type == 'file':
            for validator in field.validators:
                if isinstance(validator, FileExtensionValidator):
                    validators['fileType'] = validator.allowed_extensions
                # elif isinstance(validator, FileSizeValidator):
                #     validators['fileSize'] = validator.max_size

        if validators:
            validators.update(dict(name=field_name, type=field_type, stopMode=self.__stop_mode))
            if self.__repeater_name:
                validators['isRepeater'] = True
                validators['repeaterName'] = self.__repeater_name
        return validators

    @staticmethod
    def __get_default_values(field):
        if hasattr(field, 'default') and not type(field.default) == type:
            return field.default
        if field.initial is not None:
            return field.initial
        return ''

    def __get_field_type(self, field):
        if field.style and 'base_template' in field.style and field.style['base_template'] == 'textarea.html':
            return 'textarea'
        return self.__field_types[field.__class__.__name__]

    def __get_options(self, key, field):
        if key in self.__options:
            return self.__options[key]

        queryset, choices = None, None

        if hasattr(field, 'queryset'):
            queryset = field.queryset.all()

        if hasattr(field, 'choices'):
            choices = field.choices

        if hasattr(field, 'child_relation'):
            if hasattr(field.child_relation, 'queryset'):
                queryset = field.child_relation.queryset.all()

        if queryset and queryset.exists():
            data = []
            for inst in queryset:
                dic = {
                    'value': inst.pk,
                    'label': self.__label[key](inst) if key in self.__label else str(inst),
                }
                if key in self.__select_options_func:
                    dic.update(**self.__select_options_func[key](inst))
                if type(inst).__name__ == 'Tbl_Country_Code' and hasattr(inst, 'country_code'):
                    dic['code'] = inst.country_code
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
        'check_file': '{field} is required',
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
        return self.__enc_attrs

    def get_custom_errors(self):
        return self.__custom_errors

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
                qs = self.__model.objects.filter(**filter_dic)
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
        qs = self.__model.objects.filter(**filter_dic)
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
    #             if field in self.__country_code:
    #                 code = self.__attrs.get(self.__country_code[field], None)
    #                 code = code.country_code.replace('+', '') if code and code.country_code else None
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

    def check_file(self, *args):
        for field in args:
            value = self.__attrs.get(field, None)
            if self.__instance:
                db_value = getattr(self.__instance, field, None)
                if not db_value and not value:
                    self.__add_error(field)
            elif not value:
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
        request = self.context.get('request', None)
        if request and request.user and request.user.is_authenticated:
            if self.instance:
                if hasattr(self.Meta.model, 'modify_by'):
                    kwargs['modify_by'] = request.user
            else:
                if hasattr(self.Meta.model, 'add_by'):
                    kwargs['add_by'] = request.user

        enc_attrs = self.tsv.get_enc_attrs()
        if enc_attrs:
            kwargs.update(enc_attrs)
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
    """ Verify before Implementation """

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
        configs = ModuleConfiguration.objects.prefetch_related(
            'permissions', 'permissions__content_type').filter(
            codename__in=self.modules)
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
        q_object = Q(modules__codename__in=self.modules) | Q(perm_scope__in=['Modules', 'Global'])
        qs = CustomPermission.objects.filter(q_object)
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

    def fetch(self, *args, **kwargs):
        response = dict()
        can_view = self.request.user.has_model_perms(self.model, 'view')
        can_add = self.request.user.has_model_perms(self.model, 'add')
        can_change = self.request.user.has_model_perms(self.model, 'change')
        can_delete = self.request.user.has_model_perms(self.model, 'delete')
        can_view = can_view or can_change or can_delete

        get_data = self.has_action('get_data')
        fetch_record = self.has_action('fetch_record')

        is_form = self.has_param('is_form')
        get_perms = self.has_param('get_perms')
        get_form_configs = self.has_param('get_form_configs')
        get_title = self.has_param('get_title')

        if get_perms:
            response['permissions'] = {
                **self.get_model_permission(),
                **self.get_extra_modules_permissions(),
            }
            custom_perms = self.get_custom_permission()
            if custom_perms:
                response['permissions']['__custom'] = custom_perms

        if get_title:
            response['title'] = self.title.title()

        if get_form_configs:
            response['form_configs'] = self.get_form_configs() if (can_add or can_change) else dict()

        if get_data:
            response['data'] = self.get_list_serializer(
                self.get_queryset(), many=True).data if can_view else []

        elif fetch_record:
            if is_form:
                response['data'] = self.get_serializer(
                    self.get_object()).data if (can_add or can_change) else dict()
            else:
                response['data'] = self.get_detail_serializer(
                    self.get_object()).data if can_view else dict()

        return Response(response, status=status.HTTP_200_OK)


# noinspection PyUnresolvedReferences
class TechnoCreateMixin:

    def create(self, request, *args, **kwargs):
        s = self.get_serializer(data=self.get_payload_data())
        s.is_valid(raise_exception=True)
        inst = s.save()
        return Response({
            'data': self.get_list_serializer(inst).data if request.user.has_model_perms(self.model, 'view') else dict(),
            'message': f"{self.title} Created Successfully",
        }, status=status.HTTP_201_CREATED)


# noinspection PyUnresolvedReferences
class TechnoUpdateMixin:

    def update(self, request, *args, **kwargs):
        s = self.get_serializer(data=self.get_payload_data(), instance=self.get_object())
        s.is_valid(raise_exception=True)
        inst = s.save()
        return Response({
            'data': self.get_list_serializer(inst).data if request.user.has_model_perms(self.model, 'view') else dict(),
            'message': f"{self.title} Updated Successfully"
        }, status=status.HTTP_200_OK)


# noinspection PyUnresolvedReferences
class TechnoDeleteMixin:
    """
        Implement Soft delete for models having is_del attribute and Hard Delete Otherwise
    """

    def destroy(self, request, *args, **kwargs):
        data = self.get_request_data()
        ids = data.get('ids', [])
        queryset = self.model.objects.filter(pk__in=ids)
        delete_confirmation = data.get('delete_confirmation', 'False').lower() == 'true'
        td = DjangoSoftDelete(request=self.request, queryset=queryset)
        if delete_confirmation is True:
            if hasattr(queryset.model, 'is_del'):
                td.delete()
            else:
                for obj in objs:
                    obj.delete()
            return Response({
                'ids': ids,
                'delete_confirmation': delete_confirmation,
                'message': f'{td.model_name.capitalize()} Deleted Successfully'
            }, status=status.HTTP_200_OK)
        else:
            td.check_delete()
            return Response({
                'delete_confirmation': delete_confirmation,
                'delete_context': {
                    'model_name': td.model_name,
                    'msg_type': 'protect' if td.protect else 'cascade',
                    'summary': td.summary,
                    'msg': td.protect or td.result,
                }
            }, status=status.HTTP_200_OK)


class TechnoGenericBaseAPIView(GenericAPIView):
    model = None
    serializer_class = None
    list_serializer_class = None
    detail_serializer_class = None
    title = None
    modules = ()

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
        return self.model.objects.all()

    def get_object(self):
        try:
            return super().get_object()
        except:
            raise ClientException(f'{self.title} not found')

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
        raise Exception('Invalid Request')

    def get_payload_data(self):
        data = self.get_request_data().copy()
        if 'multipart/form-data' in self.request.content_type:
            payload = json.loads(data.get('data'))
            for k, v in data.items():
                if type(v) == InMemoryUploadedFile:
                    payload[k] = v
            # Need to test clear functionality
            # for k in data:
            #     if f'{k}-clear' in data and data[f'{k}-clear'] is True:
            #         data[k] = None
        return data

    def has_param(self, key):
        return self.get_request_data().get(key, 'False').lower() == 'true'

    def has_action(self, key):
        return self.get_request_data().get('action', None) == key


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
        return self.destroy(request, *args, **kwargs)
