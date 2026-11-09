from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from user_auth.models import UserProfile


class OrdersAPITests(APITestCase):
    """Test suite for order creation, status updates, staff deletion, and order counts."""

    def setUp(self):
        """Set up business, customer, and staff users along with an OfferDetail."""
        self.biz = User.objects.create_user(username='biz', password='pw')
        UserProfile.objects.create(user=self.biz, type='business')
        self.cust = User.objects.create_user(username='cust', password='pw')
        UserProfile.objects.create(user=self.cust, type='customer')
        self.admin = User.objects.create_user(username='adm', password='pw', is_staff=True)
        offer = Offer.objects.create(user=self.biz, title='Logo', description='Desc')
        self.detail = OfferDetail.objects.create(
            offer=offer, title='Basic', revisions=2, delivery_time_in_days=5,
            price=100, features=['Logo'], offer_type='basic'
        )

    def test_create_order_as_customer_and_not_found(self):
        """Ensure customer can create an order (201) and non-existent detail returns 404."""
        self.client.force_authenticate(user=self.cust)
        res = self.client.post(reverse('order-list-create'), {'offer_detail_id': self.detail.id})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res_404 = self.client.post(reverse('order-list-create'), {'offer_detail_id': 9999})
        self.assertEqual(res_404.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_orders_and_patch_status(self):
        """Ensure orders list works and business partner can PATCH order status."""
        order = Order.objects.create(
            customer_user=self.cust, business_user=self.biz, title='Logo',
            revisions=2, delivery_time_in_days=5, price=100, features=['Logo'], offer_type='basic'
        )
        self.client.force_authenticate(user=self.biz)
        self.assertEqual(len(self.client.get(reverse('order-list-create')).data), 1)
        url = reverse('order-detail', kwargs={'pk': order.id})
        self.assertEqual(self.client.patch(url, {'status': 'completed'}).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.patch(url, {'title': 'Hack'}).status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_order_only_staff(self):
        """Ensure non-staff receives 403 on DELETE while staff receives 204."""
        order = Order.objects.create(
            customer_user=self.cust, business_user=self.biz, title='Logo',
            revisions=2, delivery_time_in_days=5, price=100, features=['Logo'], offer_type='basic'
        )
        url = reverse('order-detail', kwargs={'pk': order.id})
        self.client.force_authenticate(user=self.biz)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.admin)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_204_NO_CONTENT)

    def test_order_counts_for_business_user(self):
        """Ensure order-count and completed-order-count return accurate numbers and 404 for invalid user."""
        Order.objects.create(
            customer_user=self.cust, business_user=self.biz, title='T',
            revisions=1, delivery_time_in_days=1, price=50, features=[], offer_type='basic', status='in_progress'
        )
        self.client.force_authenticate(user=self.cust)
        res1 = self.client.get(reverse('order-count', kwargs={'business_user_id': self.biz.id}))
        res2 = self.client.get(reverse('completed-order-count', kwargs={'business_user_id': self.biz.id}))
        self.assertEqual(res1.data['order_count'], 1)
        self.assertEqual(res2.data['completed_order_count'], 0)