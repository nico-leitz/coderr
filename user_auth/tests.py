from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from user_auth.models import UserProfile


class UserAuthAPITests(APITestCase):
    """TDD test suite for registration, login, and user profile endpoints."""

    def setUp(self):
        """Arrange initial business and customer users with profiles."""
        self.biz_user = User.objects.create_user(username='biz', email='b@test.de', password='pw123')
        self.biz_profile = UserProfile.objects.create(user=self.biz_user, type='business')
        self.cust_user = User.objects.create_user(username='cust', email='c@test.de', password='pw123')
        self.cust_profile = UserProfile.objects.create(user=self.cust_user, type='customer')

    def test_registration_valid_data_returns_201_and_token(self):
        """Ensure registering with valid data creates a user and returns a token."""
        data = {
            'username': 'newuser', 'email': 'new@test.de',
            'password': 'pw123', 'repeated_password': 'pw123', 'type': 'customer'
        }
        response = self.client.post(reverse('registration'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)

    def test_registration_password_mismatch_returns_400(self):
        """Ensure registration fails with 400 when passwords do not match."""
        data = {
            'username': 'u2', 'email': 'u2@test.de',
            'password': 'pw1', 'repeated_password': 'pw2', 'type': 'customer'
        }
        response = self.client.post(reverse('registration'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_duplicate_email_returns_400(self):
        """Ensure registration fails with 400 when email is already registered."""
        data = {
            'username': 'u3', 'email': 'b@test.de',
            'password': 'pw1', 'repeated_password': 'pw1', 'type': 'customer'
        }
        response = self.client.post(reverse('registration'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_valid_credentials_returns_200_and_token(self):
        """Ensure valid login credentials return 200 OK with auth token."""
        response = self.client.post(reverse('login'), {'username': 'biz', 'password': 'pw123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_login_invalid_credentials_returns_400(self):
        """Ensure invalid login credentials return 400 Bad Request."""
        response = self.client.post(reverse('login'), {'username': 'biz', 'password': 'wrong'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_retrieve_replaces_null_with_empty_strings(self):
        """Ensure retrieving a profile returns empty strings instead of null values."""
        self.client.force_authenticate(user=self.biz_user)
        response = self.client.get(reverse('profile-detail', kwargs={'pk': self.biz_user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['location'], '')

    def test_profile_retrieve_unauthenticated_returns_401(self):
        """Ensure unauthenticated requests to profile detail return 401."""
        response = self.client.get(reverse('profile-detail', kwargs={'pk': self.biz_user.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_patch_by_owner_returns_200(self):
        """Ensure profile owner can update their own profile fields."""
        self.client.force_authenticate(user=self.biz_user)
        url = reverse('profile-detail', kwargs={'pk': self.biz_user.id})
        response = self.client.patch(url, {'first_name': 'Max', 'location': 'Berlin'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['location'], 'Berlin')

    def test_profile_patch_by_non_owner_returns_403(self):
        """Ensure updating another user's profile is forbidden (403)."""
        self.client.force_authenticate(user=self.biz_user)
        url = reverse('profile-detail', kwargs={'pk': self.cust_user.id})
        response = self.client.patch(url, {'location': 'Munich'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_business_profile_list_returns_only_business_users(self):
        """Ensure business profiles endpoint returns an unpaginated list of business users."""
        self.client.force_authenticate(user=self.biz_user)
        response = self.client.get(reverse('business-profiles'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_customer_profile_list_returns_only_customers(self):
        """Ensure customer profiles endpoint returns an unpaginated list of customers."""
        self.client.force_authenticate(user=self.biz_user)
        response = self.client.get(reverse('customer-profiles'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)