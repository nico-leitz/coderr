from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from user_auth.models import UserProfile


class OrdersAPITests(APITestCase):
    """TDD test suite for order creation, status updates, deletion, and counters."""

    def setUp(self):
        """Arrange business, customer, and staff users plus an OfferDetail and Order."""
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
        self.order = Order.objects.create(
            customer_user=self.cust, business_user=self.biz, title='Logo',
            revisions=2, delivery_time_in_days=5, price=100, features=['Logo'], offer_type='basic'
        )

    def test_create_order_by_customer_returns_201(self):
        """Ensure a customer can create an order from a valid offer_detail_id."""
        self.client.force_authenticate(user=self.cust)
        response = self.client.post(reverse('order-list-create'), {'offer_detail_id': self.detail.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_order_by_business_user_returns_403(self):
        """Ensure a business user is forbidden from creating an order."""
        self.client.force_authenticate(user=self.biz)
        response = self.client.post(reverse('order-list-create'), {'offer_detail_id': self.detail.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order_non_existent_detail_returns_404(self):
        """Ensure creating an order with an unknown offer_detail_id returns 404."""
        self.client.force_authenticate(user=self.cust)
        response = self.client.post(reverse('order-list-create'), {'offer_detail_id': 9999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_orders_returns_user_related_orders(self):
        """Ensure GET /api/orders/ returns orders linked to the authenticated user."""
        self.client.force_authenticate(user=self.biz)
        response = self.client.get(reverse('order-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_patch_order_status_by_business_partner_returns_200(self):
        """Ensure the business partner can update the order status."""
        self.client.force_authenticate(user=self.biz)
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        response = self.client.patch(url, {'status': 'completed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')

    def test_patch_order_disallowed_field_returns_400(self):
        """Ensure sending fields other than status in PATCH returns 400."""
        self.client.force_authenticate(user=self.biz)
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        response = self.client.patch(url, {'title': 'Manipulated'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_order_by_non_staff_returns_403(self):
        """Ensure regular users cannot delete an order (403 Forbidden)."""
        self.client.force_authenticate(user=self.biz)
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order_by_staff_returns_204(self):
        """Ensure staff admin users can delete an order (204 No Content)."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_in_progress_order_count_returns_200(self):
        """Ensure order-count returns the number of in_progress orders for a business user."""
        self.client.force_authenticate(user=self.cust)
        response = self.client.get(reverse('order-count', kwargs={'business_user_id': self.biz.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_count'], 1)

    def test_completed_order_count_returns_200(self):
        """Ensure completed-order-count returns the number of completed orders."""
        self.client.force_authenticate(user=self.cust)
        response = self.client.get(reverse('completed-order-count', kwargs={'business_user_id': self.biz.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['completed_order_count'], 0)