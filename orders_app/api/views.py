from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders_app.models import Order
from user_auth.models import UserProfile
from .permissions import IsCustomerUser, IsOrderBusinessPartnerOrAdmin
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
)


class OrderListCreateView(generics.ListCreateAPIView):
    """List orders for current user or create a new order as a customer."""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """Return orders where the user is either customer or business partner."""
        user = self.request.user
        qs = Order.objects.select_related('customer_user', 'business_user')
        return qs.filter(Q(customer_user=user) | Q(business_user=user)).order_by('-created_at')

    def get_permissions(self):
        """Require customer profile for POST, authenticated user for GET."""
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        """Use creation serializer for POST and standard serializer for GET."""
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Update order status as business partner or delete order as staff."""
    queryset = Order.objects.select_related('customer_user', 'business_user').all()
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [IsAuthenticated, IsOrderBusinessPartnerOrAdmin]
    http_method_names = ['patch', 'delete', 'head', 'options']


class OrderCountView(APIView):
    """Return count of in_progress orders for a specific business user."""
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Validate business user existence and count active orders."""
        get_object_or_404(UserProfile, user_id=business_user_id, type='business')
        count = Order.objects.filter(business_user_id=business_user_id, status='in_progress').count()
        return Response({'order_count': count}, status=status.HTTP_200_OK)


class CompletedOrderCountView(APIView):
    """Return count of completed orders for a specific business user."""
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Validate business user existence and count completed orders."""
        get_object_or_404(UserProfile, user_id=business_user_id, type='business')
        count = Order.objects.filter(business_user_id=business_user_id, status='completed').count()
        return Response({'completed_order_count': count}, status=status.HTTP_200_OK)