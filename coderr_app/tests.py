from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from reviews_app.models import Review
from user_auth.models import UserProfile


class BaseInfoAPITests(APITestCase):
    """TDD test suite for base-info statistics, seed_db command, and models."""

    def test_base_info_returns_zero_when_empty(self):
        """Ensure base-info returns 0.0 average rating when no reviews exist."""
        response = self.client.get(reverse('base-info'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['average_rating'], 0.0)

    def test_base_info_calculates_accurate_statistics(self):
        """Ensure base-info returns accurate counts and rounded average rating."""
        biz = User.objects.create_user(username='biz', password='pw')
        UserProfile.objects.create(user=biz, type='business')
        cust = User.objects.create_user(username='cust', password='pw')
        Offer.objects.create(user=biz, title='Offer 1', description='Desc')
        Review.objects.create(business_user=biz, reviewer=cust, rating=4, description='Nice')
        response = self.client.get(reverse('base-info'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['average_rating'], 4.0)
        self.assertEqual(response.data['offer_count'], 1)

    def test_seed_db_command_populates_database(self):
        """Ensure the seed_db management command runs and creates initial records."""
        out = StringIO()
        call_command('seed_db', stdout=out)
        self.assertIn('Successfully seeded database!', out.getvalue())
        self.assertEqual(OfferDetail.objects.count(), 3)

    def test_model_string_representations_return_non_empty_strings(self):
        """Ensure __str__ methods of all models return valid string representations."""
        call_command('seed_db', stdout=StringIO())
        self.assertTrue(str(UserProfile.objects.first()))
        self.assertTrue(str(Offer.objects.first()))
        self.assertTrue(str(OfferDetail.objects.first()))
        self.assertTrue(str(Order.objects.first()))
        self.assertTrue(str(Review.objects.first()))