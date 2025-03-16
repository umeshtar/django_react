import uuid

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_dynamic.models import DynamicForm, DynamicFormRecord
from backend.settings import mongo_db
from python_files.techno_generic import ClientException


# Create your views here.
class DynamicModuleSqlView(APIView):
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
            response["data"] = list(self.db_collection.find(filter_query, self.get_query())) if can_view else []

        elif fetch_record:
            record = self.db_collection.find_one({'rec_id': self.get_request_data().get("rec_id")}, self.get_query())
            if record is None:
                raise ClientException(f"{self.title} not found")
            if is_form:
                response["data"] = record if (can_add or can_change) else dict()
            else:
                response["data"] = dict()

        return Response(response, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        payload = self.get_request_data()
        payload.update(self.get_recur_fields())
        result = self.db_collection.insert_one(payload)
        record = self.db_collection.find_one({'_id': result.inserted_id}, self.get_query())
        return Response(
            data={'data': record, 'message': f"{self.title} Created Successfully"},
            status=status.HTTP_201_CREATED
        )

    def put(self, request, *args, **kwargs):
        payload = self.get_request_data()
        rec_id = payload.pop('rec_id')
        self.db_collection.update_one(
            {'rec_id': rec_id},
            {'$set': {**payload, 'modify_by': request.user.username, 'modify_date': timezone.now()}}
        )
        record = self.db_collection.find_one({'rec_id': rec_id}, self.get_query())
        return Response(
            data={'data': record, 'message': f"{self.title} Updated Successfully"},
            status=status.HTTP_200_OK
        )

    def delete(self, request, *args, **kwargs):
        ids = self.get_request_data().getlist('ids[]', [])
        self.db_collection.update_many(
            {'rec_id': {'$in': ids}},
            {'$set': {'is_del': True, 'delete_by': request.user.username, 'delete_date': timezone.now()}}
        )
        return Response(
            data={'delete_confirmation': True, 'ids': ids,
                  'message': f"{self.title} Deleted Successfully"},
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
                configs[key]["options"] = validation.get('choices', [])
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

    def has_param(self, key):
        return self.get_request_data().get(key, "False").lower() == "true"

    def has_action(self, key):
        return self.get_request_data().get("action", None) == key

