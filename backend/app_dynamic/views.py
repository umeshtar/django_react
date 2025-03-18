import os
import uuid
from collections import defaultdict
from decimal import Decimal, ROUND_DOWN, InvalidOperation

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import UploadedFile
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_dynamic.models import DynamicForm
from backend.settings import mongo_db, MEDIA_ROOT
from python_files.techno_generic import ClientException


# Create your views here.
class DynamicModuleView(APIView):
    permission_classes = [IsAuthenticated]
    dynamic_form = None
    db_collection = None
    title = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        rec_id = self.kwargs.get('rec_id')
        self.dynamic_form = DynamicForm.objects.get(pk=rec_id)
        self.title = self.dynamic_form.name

        collection_name = str(self.dynamic_form.pk)
        if collection_name not in mongo_db.list_collection_names():
            raise Exception('Forms Collection Missing For: ', self.title)
        self.db_collection = mongo_db[collection_name]

    def get(self, request, *args, **kwargs):
        response = dict()
        can_view = self.request.user.has_dynamic_perms(self.dynamic_form, "View")
        can_add = self.request.user.has_dynamic_perms(self.dynamic_form, "Add")
        can_change = self.request.user.has_dynamic_perms(self.dynamic_form, "Change")
        can_delete = self.request.user.has_dynamic_perms(self.dynamic_form, "Delete")
        can_view = can_view or can_change or can_delete

        get_data = self.has_action("get_data")
        fetch_record = self.has_action("fetch_record")

        is_form = self.has_param("is_form")
        get_perms = self.has_param("get_perms")
        get_form_configs = self.has_param("get_form_configs")
        get_title = self.has_param("get_title")
        get_fields = self.has_param("get_fields") or True

        filter_query = self.get_request_data().get('filter_query', dict())
        if 'is_del' not in filter_query:
            filter_query['is_del'] = False

        if get_perms:
            response["permissions"] = {
                '__add': can_add,
                '__change': can_change,
                '__view': can_view,
                '__delete': can_delete,
            }

        if get_title:
            response["title"] = self.title

        if get_form_configs:
            response["form_configs"] = (
                self.get_form_configs(self.dynamic_form) if (can_add or can_change) else dict()
            )

        if get_fields:
            response['fields'] = {row.codename: row.name for row in self.dynamic_form.fields.all()}

        if get_data:
            response['data'] = self.get_serialized_data(
                data=list(self.db_collection.find(filter_query, self.get_query())) if can_view else [],
                is_form=False
            )

        elif fetch_record:
            record = self.db_collection.find_one({'rec_id': self.get_request_data().get("rec_id")}, self.get_query())
            if record is None:
                raise ClientException(f"{self.title} not found")
            if is_form:
                response["data"] = self.get_serialized_data(
                    data=record, is_form=is_form
                ) if (can_add or can_change) else dict()
            else:
                response["data"] = self.get_serialized_data(
                    data=record, is_form=is_form
                ) if can_view else dict()

        return Response(response, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        payload = self.get_request_data()
        form_data = self.get_validated_form_data(payload)
        form_data.update(self.get_recur_fields())
        result = self.db_collection.insert_one(form_data)
        record = self.db_collection.find_one({'_id': result.inserted_id}, self.get_query())

        data = self.get_serialized_data(data=record)
        message = f"{self.title} Created Successfully"
        return Response(data={'data': data, 'message': message}, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        payload = self.get_request_data()
        rec_id = payload.get('rec_id')
        form_data = self.get_validated_form_data(payload)
        self.db_collection.update_one(
            {'rec_id': rec_id, 'is_del': False},
            {'$set': {**form_data, 'modify_by': request.user.username, 'modify_date': timezone.now()}}
        )
        record = self.db_collection.find_one({'rec_id': rec_id}, self.get_query())

        data = self.get_serialized_data(data=record)
        message = f"{self.title} Updated Successfully"
        return Response(data={'data': data, 'message': message}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        ids = self.get_request_data().getlist('ids[]', [])
        self.db_collection.update_many(
            {'rec_id': {'$in': ids}},
            {'$set': {'is_del': True, 'delete_by': request.user.username, 'delete_date': timezone.now()}}
        )

        message = f"{self.title} Deleted Successfully"
        return Response(data={'delete_confirmation': True, 'ids': ids, 'message': message}, status=status.HTTP_200_OK)

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
                configs[key]['options'] = []
                relation_type = validation.get('relation_type', 'Choices')
                if relation_type == 'Choices':
                    configs[key]['options'] = [{'value': row, 'label': row} for row in validation.get('choices', [])]

                elif relation_type in ['One To One', 'Many To One', 'Many To Many']:
                    related_model_type = validation.get('related_model_type', None)
                    related_model = validation.get('related_model', None)
                    if related_model and related_model_type:
                        if related_model_type == 'SQL':
                            configs[key]['options'] = [
                                {'value': row.pk, 'label': str(row)}
                                for row in ContentType.objects.get(pk=related_model).model_class().objects.all()
                            ]

                        elif related_model_type == 'NoSQL':
                            related_dynamic_form = DynamicForm.objects.get(pk=related_model)
                            title_field = related_dynamic_form.validation.get('title_field')
                            configs[key]['options'] = [
                                {'value': row.get('rec_id'), 'label': row.get(title_field)}
                                for row in mongo_db[str(related_model)].find({'is_del': False}, {'_id': 0, 'rec_id': 1, title_field: 1})
                            ]

                configs[key]["multiple"] = validation.get('multiple', False)
            default_values[key] = validation.get('default', None)
        return {
            "fields": configs,
            "defaultValues": default_values,
        }

    def get_recur_fields(self):
        return dict(
            rec_id=str(uuid.uuid4()),
            add_by=self.request.user.username,
            add_date=timezone.now(),
            modify_by=None,
            modify_date=None,
            delete_by=None,
            delete_date=None,
            is_del=False,
        )

    def get_query(self, extra=None):
        if extra is None:
            extra = dict()
        return {
            '_id': 0, 'rec_id': 1,
            **{row: 1 for row in self.dynamic_form.fields.values_list('codename', flat=True)},
            **extra,
        }

    def get_validated_form_data(self, payload):
        fields = self.dynamic_form.fields.all()
        errors = defaultdict(list)
        saved_files = []
        form_data = dict()

        for field in fields:
            key = field.codename
            validation = field.validation

            if field.field_type == 'file':
                value = self.request.FILES.get(key, None)
            else:
                value = payload.get(key, None)

            form_data[key] = value

            required = validation.get('required', False)
            if required is True:
                if isinstance(value, str):
                    if value and value.strip():
                        form_data[key] = value = value.strip()
                    else:
                        errors[key].append(f"{field.name} is required")
                elif not value:
                    errors[key].append(f"{field.name} is required")

            elif isinstance(value, str) and value:
                form_data[key] = value = value.strip()

            if value:
                unique = validation.get('unique', False)
                if unique is True:
                    query = {key: {'$regex': f"^{value}$", '$options': 'i'}, 'is_del': False}
                    rec_id = payload.get('rec_id', None)
                    if rec_id:
                        query['rec_id'] = {'$ne': rec_id}
                    exists = self.db_collection.find_one(query)
                    if exists:
                        errors[key].append(f"{field.name} is already exists")

                if field.field_type in ['text', 'email', 'url']:
                    if isinstance(value, str):
                        min_length = validation.get('min_length', 0)
                        max_length = validation.get('max_length', 99999)
                        if len(value) < min_length or len(value) > max_length:
                            errors[key].append(f"{field.name} length shall be in range of {min_length} to {max_length}")
                    else:
                        errors[key].append(f"{field.name} shall be a string")

                elif field.field_type == 'number':
                    number_type = validation.get('number_type', 'int')
                    min_value = validation.get('min_value', -99999)
                    max_value = validation.get('max_value', 99999)
                    if number_type == 'int':
                        try:
                            form_data[key] = value = int(float(value))
                        except ValueError:
                            form_data[key] = value = None
                            errors[key].append(f"{field.name} is not a valid integer")

                    elif number_type == 'float':
                        try:
                            form_data[key] = value = float(value)
                        except ValueError:
                            form_data[key] = value = None
                            errors[key].append(f"{field.name} is not a valid float number")

                    elif number_type == 'decimal':
                        decimal_places = validation.get('decimal_places', 2)
                        try:
                            form_data[key] = value = str(Decimal(value).quantize(Decimal(f"1.{'0' * decimal_places}"), rounding=ROUND_DOWN))
                        except (ValueError, InvalidOperation):
                            form_data[key] = value = None
                            errors[key].append(f"{field.name} is not a valid decimal number")

                    if value is not None and (Decimal(value) < min_value or Decimal(value) > max_value):
                        errors[key].append(f"{field.name} value shall be in range of {min_value} to {max_value}")

                elif field.field_type == 'select':
                    relation_type = validation.get('relation_type', None)
                    if relation_type is None:
                        errors[key].append(f"Select valid Relation")
                    else:
                        if relation_type == 'Choices':
                            choices = validation.get('choices', [])
                            multiple = validation.get('multiple', False)
                            if multiple is True and isinstance(value, list):
                                for v in value:
                                    if v not in choices:
                                        errors[key].append(f"{v} is not a valid choice")
                            elif multiple is False:
                                if value not in choices:
                                    errors[key].append(f"{value} is not a valid choice")

                        elif relation_type in ['One To One', 'One To Many', 'Many To Many']:
                            related_model_type = validation.get('related_model_type', None)
                            if related_model_type is None:
                                raise Exception('Missing Related Model Type')

                            related_model = validation.get('related_model', None)
                            if related_model is None:
                                raise Exception('Missing Related Model')

                            if related_model_type == 'SQL':
                                try:
                                    ContentType.objects.get(pk=related_model).model_class().objects.get(pk=value)
                                except (ObjectDoesNotExist, ValueError, TypeError):
                                    errors[key].append(f"{value} is not a valid choice")

                            elif related_model_type == 'NoSQL':
                                try:
                                    DynamicForm.objects.get(pk=related_model)
                                    exists = mongo_db[str(related_model)].find_one({'rec_id': value})
                                    if exists is None:
                                        errors[key].append(f"{value} is not a valid choice")
                                except (ObjectDoesNotExist, ValueError, TypeError):
                                    errors[key].append(f"{value} is not a valid choice")

                elif field.field_type == 'file':
                    if isinstance(value, UploadedFile):
                        allowed_extensions = validation.get('allowed_extensions', '').split(',')
                        max_size = validation.get('file_size', 5 * 1024 * 1024)
                        if value.content_type not in allowed_extensions:
                            errors[key].append(f"{value.content_type} is not allowed")

                        if value.size > max_size:
                            errors[key].append(f"File size shall not be more than {max_size}")

                        if not errors[key]:
                            file_name = f"{uuid.uuid4()}_{value.name}"
                            file_path = os.path.join(MEDIA_ROOT, file_name)
                            with open(file_path, "wb") as destination:
                                for chunk in value.chunks():
                                    destination.write(chunk)
                            saved_files.append(file_path)
                            form_data[key] = file_path
                    else:
                        errors[key].append(f"Uploaded file is not valid")

            form_data.setdefault(key, validation.get('default', False if field.field_type == 'checkbox' else None))

        if errors:
            for file_path in saved_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
            raise ValidationError(errors)

        return form_data

    def get_serialized_data(self, data, is_form=False):
        if isinstance(data, list):
            return [self.get_serialized_data(row, is_form) for row in data]

        elif isinstance(data, dict):
            record = {'rec_id': data.get('rec_id')}
            for field in self.dynamic_form.fields.all():
                record[field.codename] = value = data.get(field.codename, None)
                if value:
                    if is_form is False:
                        if field.field_type == 'select':
                            relation_type = field.validation.get('relation_type', None)
                            related_model = field.validation.get('related_model', None)
                            related_model_type = field.validation.get('related_model_type', None)
                            if relation_type and related_model and related_model_type:
                                if relation_type in ['One To One', 'Many To One', 'Many To Many']:
                                    if related_model_type == 'SQL':
                                        record[field.codename] = str(ContentType.objects.get(pk=related_model).model_class().objects.get(pk=value))

                                    elif related_model_type == 'NoSQL':
                                        related_dynamic_form = DynamicForm.objects.get(pk=related_model)
                                        title_field = related_dynamic_form.validation.get('title_field', None)
                                        if title_field:
                                            record[field.codename] = mongo_db[str(related_model)].find_one(
                                                {'rec_id': value, 'is_del': False}, {title_field: 1}
                                            ).get(title_field, None)
            return record

    def has_param(self, key):
        return self.get_request_data().get(key, "False").lower() == "true"

    def has_action(self, key):
        return self.get_request_data().get("action", None) == key

