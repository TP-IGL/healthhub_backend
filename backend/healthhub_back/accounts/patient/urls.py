# urls.py

from django.urls import path
from .patient_view import PatientMedicalFileView, RetrieveQRCodeView, RetrieveQRCodeViewNSS

urlpatterns = [
    path('medical-file/<uuid:patient_id>/', 
         PatientMedicalFileView.as_view(), 
         name='patient-medical-file'),
    # RetrieveQRCodeView
    path('qr-code/<uuid:patient_id>/', 
         RetrieveQRCodeView.as_view(), 
         name='retrieve-qr-code'),
    # RetrieveQRCodeViewNSS
    path('qr-code-nss/<str:nss>/', 
         RetrieveQRCodeViewNSS.as_view(), 
         name='retrieve-qr-code-nss'),
]