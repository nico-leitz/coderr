from rest_framework import serializers
from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = OfferDetail
        fields = [
            'id', 'title', 'revisions', 'delivery_time_in_days',
            'price', 'features', 'offer_type'
        ]


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        return f"/offerdetails/{obj.id}/"


class OfferListSerializer(serializers.ModelSerializer):
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
        return {
            'first_name': obj.user.first_name or '',
            'last_name': obj.user.last_name or '',
            'username': obj.user.username
        }


class OfferRetrieveSerializer(serializers.ModelSerializer):
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
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def validate(self, data):
        if self.instance is None:
            details = data.get('details', [])
            if len(details) != 3:
                raise serializers.ValidationError({'details': 'An offer must contain exactly 3 details.'})
            types = {d.get('offer_type') for d in details}
            if types != {'basic', 'standard', 'premium'}:
                raise serializers.ValidationError({'details': 'Details must include basic, standard, and premium.'})
        else:
            if 'details' in data:
                for detail in data['details']:
                    if not detail.get('offer_type'):
                        raise serializers.ValidationError({'details': 'offer_type is required when updating details.'})
        return data

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        instance = super().update(instance, validated_data)

        if details_data is not None:
            for detail_data in details_data:
                offer_type = detail_data.get('offer_type')
                detail_obj = instance.details.filter(offer_type=offer_type).first()
                if detail_obj:
                    for attr, value in detail_data.items():
                        setattr(detail_obj, attr, value)
                    detail_obj.save()
        return instance