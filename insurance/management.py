import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'axxa_insurance.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_user('admin', 'admin@axxainsurance.com', 'admin')
    admin.is_superuser = True
    admin.is_staff = True
    admin.save()
    print('Admin user created successfully')
else:
    print('Admin user already exists')

# Create a sample customer for testing
from insurance.models import Customer
if not Customer.objects.filter(user=admin).exists():
    Customer.objects.create(user=admin, phone='123-456-7890', city='New York', state='NY')
    print('Customer profile created')
