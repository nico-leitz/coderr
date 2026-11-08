from django.db.models import Avg
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from offers_app.models import Offer
from reviews_app.models import Review
from user_auth.models import UserProfile


class BaseInfoView(APIView):
    """Return aggregated platform statistics (reviews, ratings, profiles, offers)."""
    permission_classes = [AllowAny]

    def get(self, request):
        """Calculate and return total counts and average rating rounded to 1 decimal."""
        avg = Review.objects.aggregate(avg=Avg('rating'))['avg']
        data = {
            'review_count': Review.objects.count(),
            'average_rating': round(avg, 1) if avg is not None else 0.0,
            'business_profile_count': UserProfile.objects.filter(type='business').count(),
            'offer_count': Offer.objects.count(),
        }
        return Response(data, status=status.HTTP_200_OK)