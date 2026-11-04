from django.db.models import Min
from rest_framework import generics, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from offers_app.models import Offer, OfferDetail
from .permissions import IsBusinessUser, IsOfferOwnerOrReadOnly
from .pagination import OfferPagination
from .filters import OfferFilter
from .serializers import (
    OfferDetailSerializer,
    OfferListSerializer,
    OfferRetrieveSerializer,
    OfferCreateUpdateSerializer
)


class OfferListCreateView(generics.ListCreateAPIView):
    pagination_class = OfferPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    ordering = ['-updated_at']

    def get_queryset(self):
        return Offer.objects.select_related('user').prefetch_related('details').annotate(
            min_price=Min('details__price'),
            min_delivery_time=Min('details__delivery_time_in_days')
        )

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsBusinessUser()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OfferCreateUpdateSerializer
        return OfferListSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)