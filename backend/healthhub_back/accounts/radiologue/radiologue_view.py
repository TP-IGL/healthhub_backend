from django.shortcuts import get_object_or_404
from django.db.models import Q, Prefetch
from django_filters import rest_framework as filters
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import SearchFilter

from healthhub_back.models import ResultatRadio, Examen
from .radiologue_serializers import RadiologueExamenDetailSerializer, ResultatRadioSerializer
from .radiologue_service import upload_image



############################################################################################################################################################################


class IsRadiologue(permissions.BasePermission):
    """
    Allows access only to users with role 'infermier'.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.role == 'radiologue' or request.user.role == 'Radiologue') 
        )
    
class ExamenFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=[
        ('planifie', 'Planifié'),
        ('en_cours', 'En Cours'),
        ('annule', 'Annulé'),
    ])
    type_radio = filters.ChoiceFilter(choices=ResultatRadio.RESRADIO_TYPE_CHOICES)

    class Meta:
        fields = ['status', 'type_radio']  # Define fields used in the filter

    @property
    def qs(self):
        queryset = super().qs
        # Custom logic to combine filtering from Examen and ResultatRadio
        examen_filter = Examen.objects.filter(status=self.data.get('status', None))
        resultat_radio_filter = ResultatRadio.objects.filter(type_radio=self.data.get('type_radio', None))
        combined_query = queryset & examen_filter & resultat_radio_filter
        return combined_query
    

class HistoryExamenFilter(filters.FilterSet):
    type_radio = filters.ChoiceFilter(choices=ResultatRadio.RESRADIO_TYPE_CHOICES)

    class Meta:
        model = Examen
        fields = ['type_radio']


############################################################################################################################################################################
class ExamenRadiologue(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsRadiologue]
    # get number of uploaded images , number of exams done , number of exams in progress, repartition of radio types %
    def get(self, request):
        radiologue = request.user.radiologue
        examens = Examen.objects.filter(radiologue=radiologue)
        examens_done = examens.filter(etat='termine').count()
        examens_in_progress = examens.filter(etat='en_cours').count()
        examens_planned = examens.filter(etat='planifie').count()
        examens_cancelled = examens.filter(etat='annule').count()
        examens_total = examens.count()

        # get number of uploaded images
        uploaded_images = 0
        for examen in examens:
            uploaded_images += examen.resultatradio_set.count()

        # get repartition of radio types
        radio_types = ResultatRadio.RESRADIO_TYPE_CHOICES
        radio_types_count = {}
        for radio_type in radio_types:
            radio_types_count[radio_type[1]] = examens.filter(resultatradio__type=radio_type[0]).count()

        data = {
            'examens_total': examens_total,
            'examens_done': examens_done,
            'examens_demands': examens_in_progress + examens_planned,
            # 'examens_in_progress': examens_in_progress,
            # 'examens_planned': examens_planned,
            # 'examens_cancelled': examens_cancelled,
            'uploaded_images': uploaded_images,
            'radio_types_count': radio_types_count,
        }

        return Response(data, status=status.HTTP_200_OK)



class RadiologueExamenListView(generics.ListAPIView):
    """
    Allows the nurse to view all activities they are associated with, including activity and patient details,
    with filtering, searching, and pagination.
    """
    permission_classes = [permissions.IsAuthenticated, IsRadiologue]
    serializer_class = RadiologueExamenDetailSerializer

    filter_backends = [filters.DjangoFilterBackend, SearchFilter]
    filterset_class = ExamenFilter

    def get_queryset(self):
        """
        Filter activities based on parameters like status, type of activity, and search query.
        """
        # Get nurse's activities that are associated with this nurse
        radiologue = self.request.user.radiologue
        queryset = Examen.objects.filter(
            radiologue=radiologue
        ).select_related(
            'consultation__dossier__patient'
        ).prefetch_related(
            Prefetch('resultatradio_set', queryset=ResultatRadio.objects.all())
        ).distinct()


        if self.request.GET.get('status'):
            status = self.request.GET.get('status')
            queryset = queryset.filter(etat=status)

        if self.request.GET.get('type_radio'):
            type_radio = self.request.GET.get('type_radio')
            queryset = queryset.filter(resultatradio__type=type_radio)

        if self.request.GET.get('search'):
            search_query = self.request.GET.get('search')
            queryset = queryset.filter(
                Q(consultation__dossier__patient__nom__icontains=search_query) |
                Q(consultation__dossier__patient__prenom__icontains=search_query) |
                Q(consultation__dossier__patient__NSS__icontains=search_query)
            ).distinct()

        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response(
                {'message': 'No examens found using these search filters.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        data = []
        
        for examen in queryset:
            consultation = examen.consultation
            patient = consultation.dossier.patient

            # Serialize multiple ResultatRadio objects if they exist
            serialized_data = RadiologueExamenDetailSerializer({
                'patient': patient,
                'examen': examen,
                'resultatRadio': examen.resultatradio_set.all() , 
                'consultation': consultation,
            }).data

            data.append(serialized_data)

        return Response(data, status=status.HTTP_200_OK)
    

class StartExamenView(APIView):
    """
    Allows the nurse to start an activity.
    """
    permission_classes = [permissions.IsAuthenticated, IsRadiologue]

    def patch(self, request, *args, **kwargs):
        examenID = kwargs.get("examen_id")
        examen = get_object_or_404(Examen, examenID=examenID)        
        # Update the status
        examen.etat = 'en_cours'
        examen.save()
        
        return Response(
            {'message': 'Examen started successfully.'},
            status=status.HTTP_200_OK
        )



class CreateResultatRadioView(generics.CreateAPIView):
    """
    Allows the nurse to create a radiology result.
    """
    permission_classes = [permissions.IsAuthenticated, IsRadiologue]
    serializer_class = ResultatRadioSerializer

    def post(self, request, *args, **kwargs):
        examenID = kwargs.get('examen_id')
        examen = get_object_or_404(Examen, examenID=examenID)
        
        # Check if the activity has already been completed
        if examen.etat == 'termine':
            return Response(
                {'message': 'Examen has already been completed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        

        data = request.data
        data['radioImgURL'] = upload_image(request.data['radioImgURL'])

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(examen_id=examen.examenID)
        
        return Response(
            {'message': 'Radiology result created successfully.'},
            status=status.HTTP_201_CREATED
        )




class ValidateExamenView(APIView):
    """
    Allows the nurse to validate an activity.
    """
    permission_classes = [permissions.IsAuthenticated, IsRadiologue]

    def patch(self, request, *args, **kwargs):
        examenID = kwargs.get('examen_id')
        examen = get_object_or_404(Examen, examenID=examenID)
        
        # Update the status
        examen.etat = 'termine'
        examen.save()
        
        return Response(
            {'message': 'Examen validated successfully.'},
            status=status.HTTP_200_OK
        )
    

class HistoriqueExamenView (generics.ListAPIView):
    """
    Allows the nurse to view all activities they have completed.
    """
    permission_classes = [permissions.IsAuthenticated, IsRadiologue]
    serializer_class = RadiologueExamenDetailSerializer

    filter_backends = [filters.DjangoFilterBackend, SearchFilter]
    filterset_class = HistoryExamenFilter

    def get_queryset(self):
        # Get nurse's activities
        radiologue = self.request.user.radiologue
        queryset = Examen.objects.filter(
            radiologue=radiologue,
            etat='termine'
        ).select_related(
            'consultation__dossier__patient'
        ).distinct()
    
        if self.request.GET.get('type_radio'):
            type_radio = self.request.GET.get('type_radio')
            queryset = queryset.filter(resultatradio__type=type_radio)

        if self.request.GET.get('search'):
            search_query = self.request.GET.get('search')
            queryset = queryset.filter(
                Q(consultation__dossier__patient__nom__icontains=search_query) |
                Q(consultation__dossier__patient__prenom__icontains=search_query) |
                Q(consultation__dossier__patient__NSS__icontains=search_query)
            ).distinct()

    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response(
                {'message': 'No examens found for this radiologist.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        data = []
        for examen in queryset:
            consultation = examen.consultation
            patient = consultation.dossier.patient

            serialized_data = RadiologueExamenDetailSerializer({
                'patient': patient,
                'examen': examen,
                'resultatRadio': examen.resultatRadio if hasattr(examen, 'resultatRadio') else None,
                'consultation': consultation,
            }).data

            data.append(serialized_data)

        return Response(data, status=status.HTTP_200_OK)
    
    
