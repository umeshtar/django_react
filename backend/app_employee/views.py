from app_employee.serializers import *
from python_files.techno_generic import TechnoGenericAPIView, ReactHookForm


# Create your views here.
class EmployeeView(TechnoGenericAPIView):
    model = Employee
    serializer_class = EmployeeSerializer
    modules = ('Employee',)


class DepartmentView(TechnoGenericAPIView):
    model = Department
    serializer_class = DepartmentNewSerializer
    list_serializer_class = DepartmentNewListSerializer
    employee_serializer_class = EmployeeNewSerializer
    candidate_serializer_class = CandidateNewSerializer
    section_serializer_class = SectionNewSerializer
    modules = ('Department',)

    def get_employee_serializer(self, *args, **kwargs):
        kwargs.setdefault('context', self.get_serializer_context())
        return self.employee_serializer_class(*args, **kwargs)

    def get_candidate_serializer(self, *args, **kwargs):
        kwargs.setdefault('context', self.get_serializer_context())
        return self.candidate_serializer_class(*args, **kwargs)

    def get_section_serializer(self, *args, **kwargs):
        kwargs.setdefault('context', self.get_serializer_context())
        return self.section_serializer_class(*args, **kwargs)

    def get_form_configs(self):
        form_configs = ReactHookForm(serializer=self.get_serializer_class()).get_configs(exclude=['employees', 'candidates', 'sections'])
        form_configs['repeaters'] = dict()

        form_configs['repeaters']['employees'] = ReactHookForm(serializer=self.employee_serializer_class).get_configs()
        form_configs['repeaters']['candidates'] = ReactHookForm(serializer=self.candidate_serializer_class).get_configs()
        form_configs['repeaters']['sections'] = ReactHookForm(serializer=self.section_serializer_class).get_configs()

        form_configs['defaultValues']['employees'] = []
        form_configs['defaultValues']['candidates'] = []
        form_configs['defaultValues']['sections'] = []
        return form_configs







