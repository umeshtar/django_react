from rest_framework.routers import DefaultRouter, SimpleRouter

from app_company.views import IndexViewSet

app_name = 'company'

router = SimpleRouter()
router.register('company', IndexViewSet, basename='company')

urlpatterns = router.urls
print(f'{urlpatterns=}')




