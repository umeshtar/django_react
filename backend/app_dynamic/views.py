from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_dynamic.models import DynamicForm, DynamicFormRecord


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

