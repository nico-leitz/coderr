from rest_framework import serializers
from rest_framework.exceptions import NotFound

from offers_app.models import OfferDetail
from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Read-only serializer for full Order representation."""
    price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user', 'title',
            'revisions', 'delivery_time_in_days', 'price',
            'features', 'offer_type', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = fields


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating an Order from an OfferDetail ID."""
    offer_detail_id = serializers.IntegerField(required=True)

    def validate_offer_detail_id(self, value):
        """Fetch OfferDetail with related offer creator or raise 404 NotFound."""
        try:
            detail = OfferDetail.objects.select_related('offer__user').get(id=value)
        except OfferDetail.DoesNotExist:
            raise NotFound(detail="OfferDetail with the given ID was not found.")
        self.context['offer_detail'] = detail
        return value

    def create(self, validated_data):
        """Create a new in_progress Order copying fields from the OfferDetail."""
        d = self.context['offer_detail']
        return Order.objects.create(
            customer_user=self.context['request'].user, business_user=d.offer.user,
            title=d.title, revisions=d.revisions,
            delivery_time_in_days=d.delivery_time_in_days, price=d.price,
            features=d.features, offer_type=d.offer_type, status='in_progress'
        )

    def to_representation(self, instance):
        """Return full order representation after creation."""
        return OrderSerializer(instance, context=self.context).data


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer restricting order updates strictly to the status field."""
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES, required=True)

    class Meta:
        model = Order
        fields = ['status']

    def validate(self, data):
        """Reject requests containing fields other than status."""
        received_keys = set(self.initial_data.keys())
        if not received_keys or not received_keys.issubset({'status'}):
            raise serializers.ValidationError("Only the 'status' field is allowed to be updated.")
        return data

    def to_representation(self, instance):
        """Return full order representation after status update."""
        return OrderSerializer(instance, context=self.context).data