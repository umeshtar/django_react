from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_system.models import ModuleConfiguration


# Create your views here.
class IndexView(APIView):
    permission_classes = [IsAuthenticated]
    model = ModuleConfiguration

    def get(self, request, *args, **kwargs):
        print(request.user)
        return Response({'data': 'test'})





