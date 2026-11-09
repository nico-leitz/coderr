from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer
from reviews_app.models import Review
from user_auth.models import UserProfile


class BaseInfoAPITests(APITestCase):
    """Test suite for the public platform statistics endpoint (/api/base-info/)."""

    def test_base_info_statistics(self):
        """Ensure base-info returns accurate counts and rounded average rating."""
        biz = User.objects.create_user(username='biz', password='pw')
        UserProfile.objects.create(user=biz, type='business')
        cust = User.objects.create_user(username='cust', password='pw')
        Offer.objects.create(user=biz, title='Offer 1', description='Desc')
        Review.objects.create(business_user=biz, reviewer=cust, rating=4, description='Nice')
        res = self.client.get(reverse('base-info'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['review_count'], 1)
        self.assertEqual(res.data['average_rating'], 4.0)
        self.assertEqual(res.data['business_profile_count'], 1)
        self.assertEqual(res.data['offer_count'], 1)