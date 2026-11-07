from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from user_auth.models import UserProfile
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from reviews_app.models import Review

class Command(BaseCommand):
    help = 'Seeds the database with test data for Coderr.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Deleting old test data...')
        Review.objects.all().delete()
        Order.objects.all().delete()
        OfferDetail.objects.all().delete()
        Offer.objects.all().delete()
        User.objects.filter(username__in=['max_business', 'customer_jane']).delete()

        self.stdout.write('Creating users and profiles...')
        
        business_user = User.objects.create_user(
            username='max_business',
            email='max@business.de',
            password='test1234!',
            first_name='Max',
            last_name='Mustermann'
        )
        UserProfile.objects.create(
            user=business_user,
            type='business',
            location='Berlin',
            tel='123456789',
            description='Professional web design and branding services.',
            working_hours='9-17'
        )

        customer_user = User.objects.create_user(
            username='customer_jane',
            email='jane@customer.de',
            password='test1234!',
            first_name='Jane',
            last_name='Doe'
        )
        UserProfile.objects.create(
            user=customer_user,
            type='customer',
            location='Munich'
        )

        self.stdout.write('Creating offers...')
        offer = Offer.objects.create(
            user=business_user,
            title='Website Design & Development',
            description='I will build a modern, responsive website for your business.',
        )

        OfferDetail.objects.create(
            offer=offer,
            title='Basic Landing Page',
            revisions=2,
            delivery_time_in_days=5,
            price=150.00,
            features=['1 Page', 'Responsive Design'],
            offer_type='basic'
        )

        standard_detail = OfferDetail.objects.create(
            offer=offer,
            title='Standard Corporate Site',
            revisions=5,
            delivery_time_in_days=14,
            price=450.00,
            features=['Up to 5 Pages', 'Responsive Design', 'Contact Form'],
            offer_type='standard'
        )

        OfferDetail.objects.create(
            offer=offer,
            title='Premium E-Commerce',
            revisions=10,
            delivery_time_in_days=30,
            price=1200.00,
            features=['Full E-Commerce', 'Payment Gateway', 'Admin Panel', 'SEO Setup'],
            offer_type='premium'
        )

        self.stdout.write('Creating orders...')
        Order.objects.create(
            customer_user=customer_user,
            business_user=business_user,
            title=standard_detail.title,
            revisions=standard_detail.revisions,
            delivery_time_in_days=standard_detail.delivery_time_in_days,
            price=standard_detail.price,
            features=standard_detail.features,
            offer_type=standard_detail.offer_type,
            status='in_progress'
        )

        self.stdout.write('Creating reviews...')
        Review.objects.create(
            business_user=business_user,
            reviewer=customer_user,
            rating=5,
            description='Incredible work! Fast and highly professional.'
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))
        self.stdout.write('You can now log in with:')
        self.stdout.write('- max_business (Password: test1234!)')
        self.stdout.write('- customer_jane (Password: test1234!)')