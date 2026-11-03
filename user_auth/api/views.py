from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from user_auth.models import UserProfile
from .permissions import IsProfileOwnerOrReadOnly
from .serializers import RegistrationSerializer, LoginSerializer, UserProfileSerializer, BusinessProfileListSerializer

class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token, created = Token.objects.get_or_create(user=user)

        data = {
            'token': token.key,
            'username': user.username,
            'email': user.email,
            'user_id': user.id
        }

        return Response(data, status=status.HTTP_201_CREATED)


class LoginView(ObtainAuthToken):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})

        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            data = {
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id
            }
            return Response(data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.select_related('user').all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwnerOrReadOnly]
    lookup_field = 'user__id'
    lookup_url_kwarg = 'pk'
    http_method_names = ['get', 'patch', 'head', 'options']