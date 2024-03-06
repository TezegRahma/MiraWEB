from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['cin', 'date_de_delivrance', 'email', 'phone_number','password', 'first_name', 'last_name','statut']
        extra_kwargs = {
            'password': {'write_only': True},
            'cin': {'required': True},
            'email': {'required': True},
            'phone_number': {'required': True},
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        user = User.objects.create(**validated_data)
        return user
