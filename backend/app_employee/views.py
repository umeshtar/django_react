from app_employee.serializers import *
from python_files.techno_generic import ReactHookForm, TechnoGenericAPIView


# Create your views here.
class DepartmentView(TechnoGenericAPIView):
    model = Department
    serializer_class = DepartmentSerializer
    employee_serializer_class = EmployeeSerializer
    modules = ["department"]

    def get_employee_serializer(self, *args, **kwargs):
        kwargs.setdefault("context", self.get_serializer_context())
        return self.employee_serializer_class(*args, **kwargs)

    def get_form_configs(self):
        form_configs = ReactHookForm(
            serializer=self.get_serializer_class()
        ).get_configs()
        form_configs["repeaters"] = dict()
        form_configs["repeaters"]["employees"] = ReactHookForm(
            serializer=self.employee_serializer_class
        ).get_configs(exclude=["department"])
        form_configs["defaultValues"]["employees"] = []
        return form_configs


class EmployeeView(TechnoGenericAPIView):
    model = Employee
    serializer_class = EmployeeSerializer
    modules = ["employee"]
