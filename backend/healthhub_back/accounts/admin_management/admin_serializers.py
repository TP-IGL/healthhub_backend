from rest_framework import serializers
from django.contrib.auth import get_user_model
from healthhub_back.models import CentreHospitalier  # Update if necessary

User = get_user_model()


# Handles user creation, ensuring required fields like password are secure and validating the role field.
class AdminUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    role = serializers.ChoiceField(choices=User.USER_ROLES)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'role', 'centreHospitalier')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data['role'],
            centreHospitalier=validated_data.get('centreHospitalier')
        )
        return user

# Used to serialize and deserialize User objects for generic use
class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'centreHospitalier')


class CentreHospitalierSerializer(serializers.ModelSerializer):
    class Meta:
        model = CentreHospitalier
        fields = ('id', 'nom', 'place')