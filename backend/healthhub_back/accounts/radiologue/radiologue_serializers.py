from rest_framework import serializers
from healthhub_back.models import (
    Patient,
    Consultation,
    Examen,
    ResultatRadio,
)



class PatientSummarySerializer(serializers.ModelSerializer):
    """
    Serializer for basic patient details.
    """
    class Meta:
        model = Patient
        fields = ['nom', 'prenom', 'NSS']


class RadiologueConsultationSummarySerializer(serializers.ModelSerializer):
    """
    Serializer for basic consultation details.
    """
    class Meta:
        model = Consultation
        fields = ['consultationID', 'dateConsultation', 'diagnostic', 'status']


class RadiologueExamenSummarySerializer(serializers.ModelSerializer):
    """
    Serializer for basic exam details.
    """
    class Meta:
        model = Examen
        fields = ['examenID', 'type', 'doctor_details', 'createdAt']


class ResultatRadioSerializer(serializers.ModelSerializer):
    """
    Serializer for radiology results.
    """
    class Meta:
        model = ResultatRadio
        fields = ['resRadioID','radioImgURL', 'type', 'rapport', 'examen']
        read_only_fields = ['resRadioID']


class RadiologueExamenDetailSerializer(serializers.Serializer):
    """
    Serializer to aggregate data from ResultatRadio, Examen, Consultation, and Patient models.
    """
    patient = PatientSummarySerializer()
    consultation = RadiologueConsultationSummarySerializer()
    examen = RadiologueExamenSummarySerializer()
    resultatRadio = ResultatRadioSerializer()

    def to_representation(self, instance):
        """
        Customize how data is serialized by including all relevant fields.
        """
        resultat_radio = instance.get('resultatRadio')
        examen = instance.get('examen')
        consultation = instance.get('consultation')
        patient = instance.get('patient')

        return {
            'patient': PatientSummarySerializer(patient).data,
            'examen': RadiologueExamenSummarySerializer(examen).data,
            'resultatRadio': ResultatRadioSerializer(resultat_radio).data if resultat_radio else {},
            'consultation': RadiologueConsultationSummarySerializer(consultation).data,
        }
