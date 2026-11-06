from rest_framework import serializers
from rest_framework.exceptions import NotFound
from offers_app.models import OfferDetail
from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
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
    offer_detail_id = serializers.IntegerField( required=True)

    def validate_offer_detail_id(self, value):
        try:
            offer_detail = OfferDetail.objects.select_related('offer__user').get(id=value)
        except OfferDetail.DoesNotExist:
            raise NotFound(detail="OfferDetail with the given ID was not found.")
        self.context['offer_detail'] = offer_detail
        return value

    def create(self, validated_data):
        offer_detail = self.context['offer_detail']
        customer = self.context['request'].user

        return Order.objects.create(
            customer_user=customer,
            business_user=offer_detail.offer.user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
            status='in_progress'
        )

    def to_representation(self, instance):
        return OrderSerializer(instance, context=self.context).data
    

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES, required=True)

    class Meta:
        model = Order
        fields = ['status']

    def validate(self, data):
        allowed_keys = {'status'}
        received_keys = set(self.initial_data.keys())
        if not received_keys or not received_keys.issubset(allowed_keys):
            raise serializers.ValidationError("Only the 'status' field is allowed to be updated.")
        return data

    def to_representation(self, instance):
        return OrderSerializer(instance, context=self.context).data