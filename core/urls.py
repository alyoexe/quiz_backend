from django.urls import path
from .views import PDFUploadView, TestView

urlpatterns = [
    path('upload-pdf/', PDFUploadView.as_view(), name='upload-pdf'),
    path('test/', TestView.as_view(), name='test'),
]
