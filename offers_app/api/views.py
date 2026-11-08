from django.db.models import Min
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from offers_app.models import Offer, OfferDetail
from .filters import OfferFilter
from .pagination import OfferPagination
from .permissions import IsBusinessUser, IsOfferOwnerOrReadOnly
from .serializers import (
    OfferCreateUpdateSerializer,
    OfferDetailSerializer,
    OfferListSerializer,
    OfferRetrieveSerializer,
)


class OfferListCreateView(generics.ListCreateAPIView):
    """List paginated offers or create a new offer as a business user."""
    queryset = Offer.objects.all()
    serializer_class = OfferListSerializer
    permission_classes = [AllowAny]
    pagination_class = OfferPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    ordering = ['-updated_at']

    def get_queryset(self):
        """Return offers with preloaded relations and annotated min values."""
        return Offer.objects.select_related('user').prefetch_related('details').annotate(
            min_price=Min('details__price'),
            min_delivery_time=Min('details__delivery_time_in_days')
        )

    def get_permissions(self):
        """Require business profile for POST, allow any user for GET."""
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsBusinessUser()]
        return [AllowAny()]

    def get_serializer_class(self):
        """Use write serializer for POST and list serializer for GET."""
        if self.request.method == 'POST':
            return OfferCreateUpdateSerializer
        return OfferListSerializer

    def perform_create(self, serializer):
        """Assign the authenticated user as creator of the offer."""
        serializer.save(user=self.request.user)


class OfferRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, partially update, or delete a specific offer."""
    queryset = Offer.objects.all()
    serializer_class = OfferRetrieveSerializer
    permission_classes = [IsAuthenticated, IsOfferOwnerOrReadOnly]
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        """Return offers with preloaded relations and annotated min values."""
        return Offer.objects.select_related('user').prefetch_related('details').annotate(
            min_price=Min('details__price'),
            min_delivery_time=Min('details__delivery_time_in_days')
        )

    def get_serializer_class(self):
        """Use write serializer for PATCH and retrieve serializer for GET."""
        if self.request.method == 'PATCH':
            return OfferCreateUpdateSerializer
        return OfferRetrieveSerializer


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """Retrieve a single OfferDetail package by ID."""
    queryset = OfferDetail.objects.select_related('offer').all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]