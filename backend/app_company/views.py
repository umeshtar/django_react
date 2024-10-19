from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet


# Create your views here.
class IndexViewSet(GenericViewSet):

    def list(self, request):
        return self.get_queryset()

    def retrieve(self, request, pk=None):
        return self.get_object()

    @action(detail=False)
    def get_data(self):
        pass


