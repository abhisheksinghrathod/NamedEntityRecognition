from django.urls import path
from .views import PDFOCRView, SplitPDFView

urlpatterns = [
    path('api/upload/', PDFOCRView.as_view(), name='pdf-upload'),
    path('api/split-pdf', SplitPDFView.as_view(), name='split_pdf_api')
]