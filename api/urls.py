from django.urls import path
from .views import PDFUploadView

urlpatterns = [
    path('api/upload/', PDFUploadView.as_view(), name='pdf-upload'),
]