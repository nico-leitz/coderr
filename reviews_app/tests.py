from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from reviews_app.models import Review
from user_auth.models import UserProfile


class ReviewsAPITests(APITestCase):
    """TDD test suite for listing, creating, updating, and deleting reviews."""

    def setUp(self):
        """Arrange business and customer users for review tests."""
        self.biz = User.objects.create_user(username='biz', password='pw')
        UserProfile.objects.create(user=self.biz, type='business')
        self.cust = User.objects.create_user(username='cust', password='pw')
        UserProfile.objects.create(user=self.cust, type='customer')
        self.other_cust = User.objects.create_user(username='cust2', password='pw')
        UserProfile.objects.create(user=self.other_cust, type='customer')

    def test_create_review_by_customer_returns_201(self):
        """Ensure a customer can create a review for a business user."""
        self.client.force_authenticate(user=self.cust)
        payload = {'business_user': self.biz.id, 'rating': 5, 'description': 'Great!'}
        response = self.client.post(reverse('review-list-create'), payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_duplicate_review_returns_400(self):
        """Ensure submitting a second review for the same business user returns 400."""
        Review.objects.create(business_user=self.biz, reviewer=self.cust, rating=4, description='First')
        self.client.force_authenticate(user=self.cust)
        payload = {'business_user': self.biz.id, 'rating': 5, 'description': 'Second'}
        response = self.client.post(reverse('review-list-create'), payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_for_non_business_user_returns_400(self):
        """Ensure reviewing a customer instead of a business user fails with 400."""
        self.client.force_authenticate(user=self.cust)
        payload = {'business_user': self.other_cust.id, 'rating': 5, 'description': 'Invalid'}
        response = self.client.post(reverse('review-list-create'), payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_reviews_filtered_by_business_user(self):
        """Ensure GET /api/reviews/ filters reviews by business_user_id."""
        Review.objects.create(business_user=self.biz, reviewer=self.cust, rating=4, description='Good')
        self.client.force_authenticate(user=self.cust)
        response = self.client.get(f"{reverse('review-list-create')}?business_user_id={self.biz.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_patch_review_by_owner_returns_200(self):
        """Ensure the review author can update rating and description."""
        review = Review.objects.create(business_user=self.biz, reviewer=self.cust, rating=4, description='Good')
        self.client.force_authenticate(user=self.cust)
        response = self.client.patch(reverse('review-detail', kwargs={'pk': review.id}), {'rating': 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 5)

    def test_patch_review_disallowed_field_returns_400(self):
        """Ensure attempting to update business_user on a review returns 400."""
        review = Review.objects.create(business_user=self.biz, reviewer=self.cust, rating=4, description='Good')
        self.client.force_authenticate(user=self.cust)
        response = self.client.patch(reverse('review-detail', kwargs={'pk': review.id}), {'business_user': 1})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_review_by_non_owner_returns_403(self):
        """Ensure another user cannot update someone else's review (403)."""
        review = Review.objects.create(business_user=self.biz, reviewer=self.cust, rating=4, description='Good')
        self.client.force_authenticate(user=self.other_cust)
        response = self.client.patch(reverse('review-detail', kwargs={'pk': review.id}), {'rating': 1})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review_by_owner_returns_204(self):
        """Ensure the review author can delete their review (204 No Content)."""
        review = Review.objects.create(business_user=self.biz, reviewer=self.cust, rating=4, description='Good')
        self.client.force_authenticate(user=self.cust)
        response = self.client.delete(reverse('review-detail', kwargs={'pk': review.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)