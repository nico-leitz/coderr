from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail
from user_auth.models import UserProfile


class OffersAPITests(APITestCase):
    """Test suite for offers and offerdetails CRUD, filtering, and permissions."""

    def setUp(self):
        """Create business and customer users and a sample offer with 3 details."""
        self.biz = User.objects.create_user(username='biz', password='pw')
        UserProfile.objects.create(user=self.biz, type='business')
        self.cust = User.objects.create_user(username='cust', password='pw')
        UserProfile.objects.create(user=self.cust, type='customer')
        self.offer = Offer.objects.create(user=self.biz, title='Web Design', description='Desc')
        self._create_sample_details()

    def _create_sample_details(self):
        """Helper to attach basic, standard, and premium details to self.offer."""
        for o_type, price in [('basic', 100), ('standard', 200), ('premium', 300)]:
            OfferDetail.objects.create(
                offer=self.offer, title=o_type, revisions=2,
                delivery_time_in_days=5, price=price, features=['F1'], offer_type=o_type
            )

    def _valid_offer_payload(self):
        """Return valid payload containing 3 details for creating a new offer."""
        return {
            'title': 'New Offer', 'description': 'New Desc',
            'details': [
                {'title': 'B', 'revisions': 1, 'delivery_time_in_days': 3, 'price': 50, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'S', 'revisions': 2, 'delivery_time_in_days': 5, 'price': 100, 'features': ['A'], 'offer_type': 'standard'},
                {'title': 'P', 'revisions': 3, 'delivery_time_in_days': 7, 'price': 150, 'features': ['A'], 'offer_type': 'premium'},
            ]
        }

    def test_offer_list_and_filters(self):
        """Ensure offer list is public, paginated, and supports filter parameters."""
        url = f"{reverse('offer-list-create')}?creator_id={self.biz.id}&min_price=50&max_delivery_time=10"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 1)

    def test_offer_create_business_vs_customer(self):
        """Ensure only business users can create offers (201) and customers get 403."""
        self.client.force_authenticate(user=self.cust)
        res_cust = self.client.post(reverse('offer-list-create'), self._valid_offer_payload(), format='json')
        self.assertEqual(res_cust.status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.biz)
        res_biz = self.client.post(reverse('offer-list-create'), self._valid_offer_payload(), format='json')
        self.assertEqual(res_biz.status_code, status.HTTP_201_CREATED)

    def test_offer_create_invalid_details_count(self):
        """Ensure creating an offer with fewer than 3 details returns 400 Bad Request."""
        self.client.force_authenticate(user=self.biz)
        bad_payload = {'title': 'T', 'description': 'D', 'details': []}
        res = self.client.post(reverse('offer-list-create'), bad_payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_offer_retrieve_patch_and_delete(self):
        """Ensure retrieving, partially updating details, and deleting an offer work properly."""
        self.client.force_authenticate(user=self.biz)
        url = reverse('offer-detail', kwargs={'pk': self.offer.id})
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)
        patch_data = {'title': 'Updated', 'details': [{'offer_type': 'basic', 'price': 120}]}
        self.assertEqual(self.client.patch(url, patch_data, format='json').status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_204_NO_CONTENT)

    def test_offerdetail_retrieve(self):
        """Ensure authenticated user can retrieve a specific OfferDetail by ID."""
        self.client.force_authenticate(user=self.cust)
        detail = self.offer.details.first()
        res = self.client.get(reverse('offerdetail-detail', kwargs={'pk': detail.id}))
        self.assertEqual(res.status_code, status.HTTP_200_OK)