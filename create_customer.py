import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cardealership.settings')
django.setup()

from core.models import User, Customer

def create_customer():
    # Create user
    user = User.objects.create_user(
        username='customer',
        password='customer123',
        email='customer@example.com',
        role=User.Role.CUSTOMER
    )
    
    # Create customer profile
    customer = Customer.objects.create(user=user)
    print(f"Created customer: {customer}")

if __name__ == '__main__':
    create_customer() 