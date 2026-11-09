from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail
from user_auth.models import UserProfile


class OffersAPITests(APITestCase):
    """TDD test suite for offers and offerdetails endpoints."""

    def setUp(self):
        """Arrange business and customer users and one offer with 3 details."""
        self.biz = User.objects.create_user(username='biz', password='pw')
        UserProfile.objects.create(user=self.biz, type='business')
        self.cust = User.objects.create_user(username='cust', password='pw')
        UserProfile.objects.create(user=self.cust, type='customer')
        self.offer = Offer.objects.create(user=self.biz, title='Web Design', description='Desc')
        self._create_sample_details()

    def _create_sample_details(self):
        """Attach basic, standard, and premium OfferDetail objects to self.offer."""
        for o_type, price in [('basic', 100), ('standard', 200), ('premium', 300)]:
            OfferDetail.objects.create(
                offer=self.offer, title=o_type, revisions=2,
                delivery_time_in_days=5, price=price, features=['F1'], offer_type=o_type
            )

    def _valid_offer_payload(self):
        """Return a valid 3-detail payload for POST /api/offers/."""
        return {
            'title': 'New Offer', 'description': 'New Desc',
            'details': [
                {'title': 'B', 'revisions': 1, 'delivery_time_in_days': 3, 'price': 50, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'S', 'revisions': 2, 'delivery_time_in_days': 5, 'price': 100, 'features': ['A'], 'offer_type': 'standard'},
                {'title': 'P', 'revisions': 3, 'delivery_time_in_days': 7, 'price': 150, 'features': ['A'], 'offer_type': 'premium'},
            ]
        }

    def test_offer_list_allows_unauthenticated_get(self):
        """Ensure GET /api/offers/ is publicly accessible and paginated."""
        response = self.client.get(reverse('offer-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_offer_list_filters_by_query_params(self):
        """Ensure creator_id, min_price, and max_delivery_time filters work."""
        url = f"{reverse('offer-list-create')}?creator_id={self.biz.id}&min_price=50&max_delivery_time=10"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_offer_create_by_business_user_returns_201(self):
        """Ensure a business user can create an offer with 3 details."""
        self.client.force_authenticate(user=self.biz)
        response = self.client.post(reverse('offer-list-create'), self._valid_offer_payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_offer_create_by_customer_returns_403(self):
        """Ensure a customer user is forbidden from creating an offer."""
        self.client.force_authenticate(user=self.cust)
        response = self.client.post(reverse('offer-list-create'), self._valid_offer_payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_offer_create_unauthenticated_returns_401(self):
        """Ensure unauthenticated POST to /api/offers/ returns 401."""
        response = self.client.post(reverse('offer-list-create'), self._valid_offer_payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_offer_create_with_fewer_than_three_details_returns_400(self):
        """Ensure creating an offer without 3 details fails with 400."""
        self.client.force_authenticate(user=self.biz)
        bad_payload = {'title': 'T', 'description': 'D', 'details': []}
        response = self.client.post(reverse('offer-list-create'), bad_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_offer_retrieve_authenticated_returns_200(self):
        """Ensure an authenticated user can retrieve offer details by ID."""
        self.client.force_authenticate(user=self.cust)
        response = self.client.get(reverse('offer-detail', kwargs={'pk': self.offer.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_offer_patch_by_owner_updates_nested_detail(self):
        """Ensure offer owner can partially update an offer and its package detail."""
        self.client.force_authenticate(user=self.biz)
        url = reverse('offer-detail', kwargs={'pk': self.offer.id})
        patch_data = {'title': 'Updated', 'details': [{'offer_type': 'basic', 'price': 120}]}
        response = self.client.patch(url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_offer_patch_detail_without_offer_type_returns_400(self):
        """Ensure updating a nested detail without specifying offer_type returns 400."""
        self.client.force_authenticate(user=self.biz)
        url = reverse('offer-detail', kwargs={'pk': self.offer.id})
        response = self.client.patch(url, {'details': [{'price': 120}]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_offer_patch_by_non_owner_returns_403(self):
        """Ensure non-owners receive 403 Forbidden when trying to PATCH an offer."""
        self.client.force_authenticate(user=self.cust)
        url = reverse('offer-detail', kwargs={'pk': self.offer.id})
        response = self.client.patch(url, {'title': 'Hack'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_offer_delete_by_owner_returns_204(self):
        """Ensure offer owner can delete their offer and receives 204 No Content."""
        self.client.force_authenticate(user=self.biz)
        url = reverse('offer-detail', kwargs={'pk': self.offer.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_offerdetail_retrieve_authenticated_returns_200(self):
        """Ensure authenticated user can retrieve a single OfferDetail object."""
        self.client.force_authenticate(user=self.cust)
        detail = self.offer.details.first()
        response = self.client.get(reverse('offerdetail-detail', kwargs={'pk': detail.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)