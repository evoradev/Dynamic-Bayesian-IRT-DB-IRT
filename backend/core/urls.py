from django.urls import path
from .views import upload_test_view

urlpatterns = [
    path('upload-test/', upload_test_view, name='upload_test'),
]