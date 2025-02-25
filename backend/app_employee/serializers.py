from django.db import transaction
from rest_framework.exceptions import ValidationError

from app_employee.models import *
from python_files.techno_delete import DjangoSoftDelete
from python_files.techno_generic import TechnoModelSerializer


class EmployeeSerializer(TechnoModelSerializer):
    class Meta:
        model = Employee
        fields = ['name', 'department']

    def techno_validate(self, attrs: dict):
        self.tsv.check_exists('name')


class DepartmentSerializer(TechnoModelSerializer):

    class Meta:
        model = Department
        fields = ['name']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        is_form = self.context.get('is_form', False)
        view = self.context.get('view')
        employees = view.get_employee_serializer(instance.employees.all(), many=True).data
        if is_form:
            data['employees'] = employees
        else:
            data['employees'] = ', '.join([row.get('name') for row in employees])
        return data

    def create(self, validated_data):
        try:
            with transaction.atomic():
                record = super().create(validated_data)

                view = self.context.get('view')
                form_errors = dict()
                payload_data = view.get_payload_data()
                data = payload_data.pop('employees', [])
                for i, row in enumerate(data):
                    row['department'] = record.pk
                    s = view.get_employee_serializer(data=row)
                    if s.is_valid():
                        s.save()
                    else:
                        for field, errors in s.errors.items():
                            form_errors[f"employees.{i}.{field}"] = ', '.join(errors)
                if form_errors:
                    raise ValidationError(form_errors)

                return record
        except Exception:
            transaction.rollback()
            raise

    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                record = super().update(instance, validated_data)

                view = self.context.get('view')
                form_errors = dict()
                payload_data = view.get_payload_data()

                qs = instance.employees.all()
                dic = {inst.pk: inst for inst in qs}
                data = payload_data.pop('employees', [])
                for i, row in enumerate(data):
                    inst = dic.pop(row.get('rec_id', 0), None)
                    if inst:
                        s = view.get_employee_serializer(data=row, instance=inst, partial=True)
                    else:
                        s = view.get_employee_serializer(data=row)
                    if s.is_valid():
                        s.save()
                    else:
                        for field, errors in s.errors.items():
                            form_errors[f"employees.{i}.{field}"] = ', '.join(errors)

                qs = qs.filter(pk__in=dic.keys())
                if qs.exists():
                    td = DjangoSoftDelete(request=view.request, queryset=qs)
                    td.check_delete()
                    if td.protect:
                        form_errors[f"employees.{i}.{field}"] = td.protect_msg
                    else:
                        td.delete()

                if form_errors:
                    raise ValidationError(form_errors)
                return record
        except Exception:
            transaction.rollback()
            raise




