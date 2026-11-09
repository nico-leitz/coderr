from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from reviews_app.models import Review
from user_auth.models import UserProfile


class ReviewsAPITests(APITestCase):
    """Test suite for listing, creating, updating, and deleting customer reviews."""

    def setUp(self):
        """Create business user and customer user for review testing."""
        self.biz = User.objects.create_user(username='biz', password='pw')
        UserProfile.objects.create(user=self.biz, type='business')
        self.cust = User.objects.create_user(username='cust', password='pw')
        UserProfile.objects.create(user=self.cust, type='customer')

    def test_create_review_and_prevent_duplicate(self):
        """Ensure a customer can create one review per business user and duplicates return 400."""
        self.client.force_authenticate(user=self.cust)
        payload = {'business_user': self.biz.id, 'rating': 5, 'description': 'Great!'}
        res1 = self.client.post(reverse('review-list-create'), payload)
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        res2 = self.client.post(reverse('review-list-create'), payload)
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_patch_and_delete_review(self):
        """Ensure reviews can be filtered, updated (rating/description only), and deleted by owner."""
        review = Review.objects.create(business_user=self.biz, reviewer=self.cust, rating=4, description='Good')
        self.client.force_authenticate(user=self.cust)
        res_list = self.client.get(f"{reverse('review-list-create')}?business_user_id={self.biz.id}")
        self.assertEqual(len(res_list.data), 1)
        url = reverse('review-detail', kwargs={'pk': review.id})
        self.assertEqual(self.client.patch(url, {'rating': 5}).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.patch(url, {'business_user': 1}).status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_204_NO_CONTENT)