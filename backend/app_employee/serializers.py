from django.db import transaction
from rest_framework.exceptions import ValidationError

from app_employee.models import *
from python_files.techno_delete import DjangoSoftDelete
from python_files.techno_generic import TechnoModelSerializer, TechnoListSerializer, decrypt_id, ClientException


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

    def techno_validate(self, attrs: dict):
        self.tsv.check_exists('name')


class EmployeeNewSerializer(TechnoModelSerializer):
    class Meta:
        model = Employee
        fields = ['name']

    def techno_validate(self, attrs: dict):
        self.tsv.check_exists('name')

    def create(self, validated_data):
        department = self.context.get('record')
        validated_data['department'] = department
        return super().create(validated_data)


class CandidateNewSerializer(TechnoModelSerializer):
    class Meta:
        model = Candidate
        fields = ['name']

    def techno_validate(self, attrs: dict):
        self.tsv.check_exists('name')

    def create(self, validated_data):
        department = self.context.get('record')
        validated_data['department'] = department
        return super().create(validated_data)


class SectionNewSerializer(TechnoModelSerializer):
    class Meta:
        model = Section
        fields = ['name']

    def techno_validate(self, attrs: dict):
        self.tsv.check_exists('name')

    def create(self, validated_data):
        record = super().create(validated_data)
        department = self.context.get('record')
        department.sections.add(record)
        return record


class DepartmentNewSerializer(TechnoModelSerializer):

    class Meta:
        model = Department
        fields = ['name']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        is_form = self.context.get('is_form', False)
        if is_form:
            view = self.context.get('view', False)
            data['employees'] = view.get_employee_serializer(instance.employees.all(), many=True).data
            data['candidates'] = view.get_candidate_serializer(instance.candidates.all(), many=True).data
            data['sections'] = view.get_section_serializer(instance.sections.all(), many=True).data
        return data

    def create(self, validated_data):
        try:
            with transaction.atomic():
                view = self.context.get('view')
                record = super().create(validated_data)

                context = {'record': record, 'error_index': 0, **view.get_serializer_context()}
                form_errors = dict()
                post_data = view.get_post_data()
                repeaters = [
                    ('employees', view.get_employee_serializer),
                    ('candidates', view.get_candidate_serializer),
                    ('sections', view.get_section_serializer),
                ]
                for name, serializer in repeaters:
                    data = post_data.pop(name, [])
                    for i, row in enumerate(data):
                        s = serializer(data=row, context=context)
                        if s.is_valid():
                            s.save()
                        else:
                            for field, errors in s.errors.items():
                                form_errors[f"{name}.{i}.{field}"] = ', '.join(errors)
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
                post_data = view.get_post_data()
                repeaters = [
                    ('employees', view.get_employee_serializer, instance.employees.all()),
                    ('candidates', view.get_candidate_serializer, instance.candidates.all()),
                    ('sections', view.get_section_serializer, instance.sections.all()),
                ]
                for name, serializer, qs in repeaters:
                    data = post_data.pop(name, [])
                    dic = {inst.pk: inst for inst in qs}
                    for i, row in enumerate(data):
                        inst = dic.pop(decrypt_id(row.get('rec_id', 0)), None)
                        s = serializer(data=row, instance=inst, partial=inst is not None)
                        if s.is_valid():
                            s.save()
                        else:
                            for field, errors in s.errors.items():
                                form_errors[f"{name}.{i}.{field}"] = ', '.join(errors)
                    objs = qs.filter(pk__in=dic.keys())
                    td = DjangoSoftDelete(view.request, qs.model, objs)
                    td.check_delete()
                    if td.protect:
                        form_errors[name] = td.protect_msg
                    else:
                        td.delete()
                if form_errors:
                    raise ValidationError(form_errors)

                return record
        except Exception:
            transaction.rollback()
            raise


class DepartmentNewListSerializer(TechnoListSerializer):

    class Meta:
        model = Department
        fields = ['name', 'employees', 'candidates', 'sections']
        extra_kwargs = {
            'employees': {'label': 'Employees'},
            'candidates': {'label': 'Candidates'},
            'sections': {'label': 'Sections'},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        view = self.context.get('view', False)
        data['employees'] = ', '.join([row.get('name') for row in view.get_employee_serializer(instance.employees.all(), many=True).data])
        data['candidates'] = ', '.join([row.get('name') for row in view.get_candidate_serializer(instance.candidates.all(), many=True).data])
        data['sections'] = ', '.join([row.get('name') for row in view.get_section_serializer(instance.sections.all(), many=True).data])
        return data



