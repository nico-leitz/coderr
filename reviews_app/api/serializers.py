from rest_framework import serializers
from user_auth.models import UserProfile
from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Review
        fields = [
            'id', 'business_user', 'reviewer', 'rating',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'reviewer', 'created_at', 'updated_at']

    def validate_business_user(self, value):
        if not UserProfile.objects.filter(user=value, type='business').exists():
            raise serializers.ValidationError("The specified user is not a business user.")
        return value

    def validate(self, data):
        request = self.context.get('request')
        if request and request.method == 'POST':
            business_user = data.get('business_user')
            if Review.objects.filter(business_user=business_user, reviewer=request.user).exists():
                raise serializers.ValidationError("You have already submitted a review for this business user.")
        return data