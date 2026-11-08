from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from reviews_app.models import Review
from user_auth.models import UserProfile


class Command(BaseCommand):
    """Management command to seed the database with initial test data."""
    help = 'Seeds the database with test data for Coderr.'

    def handle(self, *args, **kwargs):
        """Execute database seeding workflow."""
        self._clear_old_data()
        business_user = self._create_business_user()
        customer_user = self._create_customer_user()
        offer = self._create_offer(business_user)
        standard_detail = self._create_offer_details(offer)
        self._create_order_and_review(customer_user, business_user, standard_detail)
        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))

    def _clear_old_data(self):
        """Remove existing test records to avoid duplicates."""
        Review.objects.all().delete()
        Order.objects.all().delete()
        OfferDetail.objects.all().delete()
        Offer.objects.all().delete()
        User.objects.filter(username__in=['max_business', 'customer_jane']).delete()

    def _create_business_user(self):
        """Create and return a test business user with profile."""
        user = User.objects.create_user(
            username='max_business', email='max@business.de',
            password='test1234!', first_name='Max', last_name='Mustermann'
        )
        UserProfile.objects.create(
            user=user, type='business', location='Berlin', tel='123456789',
            description='Professional web design services.', working_hours='9-17'
        )
        return user

    def _create_customer_user(self):
        """Create and return a test customer user with profile."""
        user = User.objects.create_user(
            username='customer_jane', email='jane@customer.de',
            password='test1234!', first_name='Jane', last_name='Doe'
        )
        UserProfile.objects.create(user=user, type='customer', location='Munich')
        return user

    def _create_offer(self, business_user):
        """Create and return a sample offer for the business user."""
        return Offer.objects.create(
            user=business_user,
            title='Website Design & Development',
            description='I will build a modern, responsive website for your business.'
        )

    def _create_offer_details(self, offer):
        """Create basic, standard, and premium details and return standard detail."""
        OfferDetail.objects.create(
            offer=offer, title='Basic Landing Page', revisions=2,
            delivery_time_in_days=5, price=150.00, features=['1 Page'], offer_type='basic'
        )
        standard = OfferDetail.objects.create(
            offer=offer, title='Standard Corporate Site', revisions=5,
            delivery_time_in_days=14, price=450.00, features=['5 Pages', 'SEO'], offer_type='standard'
        )
        OfferDetail.objects.create(
            offer=offer, title='Premium E-Commerce', revisions=10,
            delivery_time_in_days=30, price=1200.00, features=['Full Shop'], offer_type='premium'
        )
        return standard

    def _create_order_and_review(self, customer, business, detail):
        """Create a sample order and review between customer and business user."""
        Order.objects.create(
            customer_user=customer, business_user=business, title=detail.title,
            revisions=detail.revisions, delivery_time_in_days=detail.delivery_time_in_days,
            price=detail.price, features=detail.features, offer_type=detail.offer_type
        )
        Review.objects.create(
            business_user=business, reviewer=customer, rating=5,
            description='Incredible work! Fast and highly professional.'
        )