from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from user_auth.models import UserProfile

class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True, allow_blank=False)
    type = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'password': {'write_only': True},
            'type': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({'repeated_password': 'Passwords do not match.'})
        if data.get('email') and User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'email does already exist.'})
        return data

    def create(self, validated_data):
        validated_data.pop('repeated_password', None)
        type_data = validated_data.pop('type')
        
        user = User.objects.create_user(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            password=validated_data.get('password')
        )
       
        UserProfile.objects.create(user=user, type=type_data)

        return user


class LoginSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data.get('username'), password=data.get('password'))
            
        if user:
            data['user'] = user
            return data
                
        raise serializers.ValidationError({"detail": "Invalid username or password."})