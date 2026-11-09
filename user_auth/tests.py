from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from user_auth.models import UserProfile


class UserAuthAPITests(APITestCase):
    """Test suite for registration, login, and user profile endpoints."""

    def setUp(self):
        """Create initial business and customer users with profiles."""
        self.biz_user = User.objects.create_user(username='biz', email='b@test.de', password='pw123')
        self.biz_profile = UserProfile.objects.create(user=self.biz_user, type='business')
        self.cust_user = User.objects.create_user(username='cust', email='c@test.de', password='pw123')
        self.cust_profile = UserProfile.objects.create(user=self.cust_user, type='customer')

    def test_registration_success(self):
        """Ensure a new user can register and receives a token and 201 status."""
        data = {
            'username': 'newuser', 'email': 'new@test.de',
            'password': 'pw123', 'repeated_password': 'pw123', 'type': 'customer'
        }
        response = self.client.post(reverse('registration'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)

    def test_registration_password_mismatch_and_duplicate_email(self):
        """Ensure registration fails with 400 on password mismatch or existing email."""
        bad_pw = {'username': 'u2', 'email': 'u2@test.de', 'password': '1', 'repeated_password': '2', 'type': 'customer'}
        self.assertEqual(self.client.post(reverse('registration'), bad_pw).status_code, status.HTTP_400_BAD_REQUEST)
        dup_mail = {'username': 'u3', 'email': 'b@test.de', 'password': '1', 'repeated_password': '1', 'type': 'customer'}
        self.assertEqual(self.client.post(reverse('registration'), dup_mail).status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success_and_failure(self):
        """Ensure valid login returns 200 with token and invalid login returns 400."""
        res_ok = self.client.post(reverse('login'), {'username': 'biz', 'password': 'pw123'})
        self.assertEqual(res_ok.status_code, status.HTTP_200_OK)
        res_fail = self.client.post(reverse('login'), {'username': 'biz', 'password': 'wrong'})
        self.assertEqual(res_fail.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_get_and_non_null_fields(self):
        """Ensure authenticated users can fetch profiles with empty strings instead of null."""
        self.client.force_authenticate(user=self.biz_user)
        res = self.client.get(reverse('profile-detail', kwargs={'pk': self.biz_user.id}))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['location'], '')

    def test_profile_patch_owner_vs_other(self):
        """Ensure only the profile owner can PATCH their profile, returning 403 for others."""
        self.client.force_authenticate(user=self.biz_user)
        url = reverse('profile-detail', kwargs={'pk': self.biz_user.id})
        res = self.client.patch(url, {'first_name': 'Max', 'location': 'Berlin'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        other_url = reverse('profile-detail', kwargs={'pk': self.cust_user.id})
        self.assertEqual(self.client.patch(other_url, {'location': 'X'}).status_code, status.HTTP_403_FORBIDDEN)

    def test_business_and_customer_profile_lists(self):
        """Ensure business and customer profile list endpoints return unpaginated arrays."""
        self.client.force_authenticate(user=self.biz_user)
        res_biz = self.client.get(reverse('business-profiles'))
        res_cust = self.client.get(reverse('customer-profiles'))
        self.assertEqual(res_biz.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_biz.data), 1)
        self.assertEqual(len(res_cust.data), 1)