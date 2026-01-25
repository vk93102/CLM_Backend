from django.urls import path

from .private_upload_views import PrivateUploadsUrlView, PrivateUploadsView

urlpatterns = [
    path('private-uploads/', PrivateUploadsView.as_view(), name='private-uploads'),
    path('private-uploads/url/', PrivateUploadsUrlView.as_view(), name='private-uploads-url'),
]
