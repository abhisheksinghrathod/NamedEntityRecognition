from django.urls import path
from .views import PDFOCRView

urlpatterns = [
    path('api/upload/', PDFOCRView.as_view(), name='pdf-upload'),
]