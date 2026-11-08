from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from user_auth.models import UserProfile
from .permissions import IsProfileOwnerOrReadOnly
from .serializers import (
    BusinessProfileListSerializer,
    CustomerProfileListSerializer,
    LoginSerializer,
    RegistrationSerializer,
    UserProfileSerializer,
)


class RegistrationView(generics.CreateAPIView):
    """Register a new user and return an auth token with user metadata."""
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """Validate registration data, create user, and return token payload."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        data = {'token': token.key, 'username': user.username, 'email': user.email, 'user_id': user.id}
        return Response(data, status=status.HTTP_201_CREATED)


class LoginView(ObtainAuthToken):
    """Authenticate a user and return their auth token and user details."""
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """Validate credentials and return token response with HTTP 200."""
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            data = {'token': token.key, 'username': user.username, 'email': user.email, 'user_id': user.id}
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or partially update a specific user profile by user ID."""
    queryset = UserProfile.objects.select_related('user').all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwnerOrReadOnly]
    lookup_field = 'user__id'
    lookup_url_kwarg = 'pk'
    http_method_names = ['get', 'patch', 'head', 'options']


class BusinessProfileListView(generics.ListAPIView):
    """List all user profiles of type 'business'."""
    queryset = UserProfile.objects.select_related('user').filter(type='business')
    serializer_class = BusinessProfileListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


class CustomerProfileListView(generics.ListAPIView):
    """List all user profiles of type 'customer'."""
    queryset = UserProfile.objects.select_related('user').filter(type='customer')
    serializer_class = CustomerProfileListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None