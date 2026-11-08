from rest_framework import serializers
from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """Serializer for full OfferDetail representation and validation."""
    price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = OfferDetail
        fields = [
            'id', 'title', 'revisions', 'delivery_time_in_days',
            'price', 'features', 'offer_type'
        ]
        extra_kwargs = {
            'revisions': {'required': True},
            'features': {'required': True},
        }


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """Serializer returning only ID and relative URL link for an OfferDetail."""
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        """Return relative endpoint URL for the specific offer detail."""
        return f"/offerdetails/{obj.id}/"


class OfferListSerializer(serializers.ModelSerializer):
    """Serializer for paginated offer list including creator details."""
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False, read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time', 'user_details'
        ]

    def get_user_details(self, obj):
        """Return basic profile information of the offer creator."""
        return {
            'first_name': obj.user.first_name or '',
            'last_name': obj.user.last_name or '',
            'username': obj.user.username
        }


class OfferRetrieveSerializer(serializers.ModelSerializer):
    """Serializer for retrieving a single offer with detail links."""
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False, read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time'
        ]


class OfferCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and partially updating offers with nested details."""
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def __init__(self, *args, **kwargs):
        """Propagate partial flag to nested detail serializer on PATCH requests."""
        super().__init__(*args, **kwargs)
        if self.partial and 'details' in self.fields:
            self.fields['details'].child.partial = True

    def validate_details(self, value):
        """Ensure 3 valid package types on POST and require offer_type on PATCH."""
        if self.instance is None:
            if len(value) != 3 or {d.get('offer_type') for d in value} != {'basic', 'standard', 'premium'}:
                raise serializers.ValidationError('An offer must contain basic, standard, and premium details.')
        elif any(not d.get('offer_type') for d in value):
            raise serializers.ValidationError('offer_type is required when updating details.')
        return value

    def create(self, validated_data):
        """Create offer instance and its three associated OfferDetail objects."""
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

    def update(self, instance, validated_data):
        """Update offer fields and matching OfferDetail instances."""
        for detail_data in validated_data.pop('details', []):
            detail_obj = instance.details.filter(offer_type=detail_data.get('offer_type')).first()
            if detail_obj:
                for attr, value in detail_data.items():
                    setattr(detail_obj, attr, value)
                detail_obj.save()
        instance = super().update(instance, validated_data)
        instance.refresh_from_db()
        return instance