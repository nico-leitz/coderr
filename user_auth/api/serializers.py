from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers

from user_auth.models import UserProfile


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for registering a new user and creating their UserProfile."""
    repeated_password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True, allow_blank=False)
    type = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'password': {'write_only': True},
            'type': {'write_only': True},
        }

    def validate(self, data):
        """Ensure passwords match and the email address is unique."""
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({'repeated_password': 'Passwords do not match.'})
        if data.get('email') and User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'Email already exists.'})
        return data

    def create(self, validated_data):
        """Create User instance and associated UserProfile with given type."""
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
    """Serializer for authenticating an existing user via username and password."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Authenticate credentials and attach the user to validated_data."""
        user = authenticate(username=data.get('username'), password=data.get('password'))
        if user:
            data['user'] = user
            return data
        raise serializers.ValidationError({'detail': 'Invalid username or password.'})


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for retrieving and updating detailed UserProfile information."""
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
        """Update nested User fields first, then update UserProfile fields."""
        user_data = validated_data.pop('user', {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Convert None values in text fields to empty strings as required by spec."""
        data = super().to_representation(instance)
        non_null = ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']
        for field in non_null:
            if field in data and data[field] is None:
                data[field] = ''
        return data


class BusinessProfileListSerializer(UserProfileSerializer):
    """Serializer for listing business user profiles."""

    class Meta(UserProfileSerializer.Meta):
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type'
        ]


class CustomerProfileListSerializer(UserProfileSerializer):
    """Serializer for listing customer user profiles."""
    uploaded_at = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta(UserProfileSerializer.Meta):
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'uploaded_at', 'type'
        ]