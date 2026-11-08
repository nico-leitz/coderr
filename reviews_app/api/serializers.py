from rest_framework import serializers

from reviews_app.models import Review
from user_auth.models import UserProfile


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for listing and creating customer reviews."""
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Review
        fields = [
            'id', 'business_user', 'reviewer', 'rating',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'reviewer', 'created_at', 'updated_at']

    def validate_business_user(self, value):
        """Ensure the reviewed user actually has a business profile."""
        if not UserProfile.objects.filter(user=value, type='business').exists():
            raise serializers.ValidationError("The specified user is not a business user.")
        return value

    def validate(self, data):
        """Prevent a customer from submitting multiple reviews for the same business."""
        request = self.context.get('request')
        if request and request.method == 'POST':
            if Review.objects.filter(business_user=data.get('business_user'), reviewer=request.user).exists():
                raise serializers.ValidationError("You have already reviewed this business user.")
        return data


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating only rating and description of a review."""
    rating = serializers.IntegerField(min_value=1, max_value=5, required=False)

    class Meta:
        model = Review
        fields = [
            'id', 'business_user', 'reviewer', 'rating',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'business_user', 'reviewer', 'created_at', 'updated_at']

    def validate(self, data):
        """Ensure only rating and description fields are sent in the request."""
        allowed_keys = {'rating', 'description'}
        received_keys = set(self.initial_data.keys())
        if not received_keys or not received_keys.issubset(allowed_keys):
            raise serializers.ValidationError("Only 'rating' and 'description' fields are editable.")
        return data