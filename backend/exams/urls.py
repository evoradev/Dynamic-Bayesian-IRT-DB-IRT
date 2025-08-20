from django.urls import path
from "./views/pdfUploadView.py" import pdfUploadView

urlpatterns = [
    path('upload-test/', pdfUploadView.as_view(), name='upload_pdf'),
]