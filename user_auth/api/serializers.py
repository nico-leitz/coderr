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

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False, allow_blank=True)
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True)
    email = serializers.EmailField(source='user.email', required=False)

    class Meta:
        model = UserProfile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours',
            'type', 'email', 'created_at'
        ]
        read_only_fields = ['user', 'type', 'created_at']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        non_null_fields = ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']
        for field in non_null_fields:
            if field in data and data[field] is None:
                data[field] = ''
        return data