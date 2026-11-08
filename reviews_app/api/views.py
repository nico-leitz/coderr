from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.permissions import IsAuthenticated

from reviews_app.models import Review
from .filters import ReviewFilter
from .permissions import IsCustomerUser, IsReviewOwnerOrReadOnly
from .serializers import ReviewSerializer, ReviewUpdateSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    """List filtered reviews or create a new review as a customer."""
    queryset = Review.objects.select_related('business_user', 'reviewer').all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['updated_at', 'rating']
    ordering = ['-updated_at']

    def get_permissions(self):
        """Require customer profile for POST, authenticated user for GET."""
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """Set the authenticated customer as the reviewer."""
        serializer.save(reviewer=self.request.user)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Update or delete a specific review if owned by the current user."""
    queryset = Review.objects.select_related('business_user', 'reviewer').all()
    serializer_class = ReviewUpdateSerializer
    permission_classes = [IsAuthenticated, IsReviewOwnerOrReadOnly]
    http_method_names = ['patch', 'delete', 'head', 'options']