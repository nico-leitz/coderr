from django.db.models import Avg
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from user_auth.models import UserProfile
from offers_app.models import Offer
from reviews_app.models import Review


class BaseInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        review_count = Review.objects.count()
        avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg']
        average_rating = round(avg_rating, 1) if avg_rating is not None else 0.0
        business_profile_count = UserProfile.objects.filter(type='business').count()
        offer_count = Offer.objects.count()

        data = {
            'review_count': review_count,
            'average_rating': average_rating,
            'business_profile_count': business_profile_count,
            'offer_count': offer_count,
        }
        return Response(data, status=status.HTTP_200_OK)