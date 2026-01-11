from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkflowViewSet, WorkflowInstanceViewSet

router = DefaultRouter()
router.register(r'workflows', WorkflowViewSet, basename='workflow')
router.register(r'workflow-instances', WorkflowInstanceViewSet, basename='workflow-instance')

urlpatterns = [
    path('', include(router.urls)),
]
