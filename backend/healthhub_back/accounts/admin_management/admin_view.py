# accounts/admin_management/views.py

from rest_framework import generics, permissions, viewsets, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from healthhub_back.models import CentreHospitalier, Patient
from .admin_serializers import AdminUserCreateSerializer, AdminUserSerializer, CentreHospitalierSerializer, PatientCreateSerializer
from .admin_service import create_user_account, list_all_users, get_user_by_id
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from .admin_service import PatientService
from .admin_serializers import Patient, DossierMedicalSerializer


# restrict access to admin users.
class IsAdminUserCustom(permissions.BasePermission):
    def has_permission(self, request, view):
        print(request.user)
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

# Allows admin users to create new users.
class AdminUserCreateView(generics.CreateAPIView):
    serializer_class = AdminUserCreateSerializer
    permission_classes = [IsAdminUserCustom]

    def post(self, request, *args, **kwargs):
        user = create_user_account(request.data)
        serializer = AdminUserSerializer(user)
        return Response(serializer.data, status=201)

class AdminUserListView(generics.ListAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUserCustom]

    def get_queryset(self):
        return list_all_users()

class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUserCustom]

    def get_object(self):
        user_id = self.kwargs['user_id']
        return get_user_by_id(user_id)
    

class CentreHospitalierCreateView(generics.CreateAPIView):
    serializer_class = CentreHospitalierSerializer
    queryset = CentreHospitalier.objects.all()
    permission_classes = [IsAdminUserCustom]

# Allows listing all CentreHospitalier entries
class CentreHospitalierListView(generics.ListAPIView):
    serializer_class = CentreHospitalierSerializer
    queryset = CentreHospitalier.objects.all()
    permission_classes = [IsAdminUserCustom]



class PatientCreateView(CreateAPIView):
    serializer_class = PatientCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            patient, dossier = PatientService.create_patient_with_dossier(serializer.validated_data)

            response_data = {
                'patient': PatientCreateSerializer(patient).data,
                'message': 'Patient créé avec succès',
                'dossier_id': str(dossier.dossierID)
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )