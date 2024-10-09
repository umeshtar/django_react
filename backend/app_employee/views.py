from rest_framework.response import Response
from rest_framework.views import APIView


# Create your views here.
class EmployeeView(APIView):

    def get(self, request, *args, **kwargs):
        return Response({'data': 'Hello World'})









