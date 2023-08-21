import os
import django
import sys
import random
import string

def generate_random_name():
    # Generate a random name using letters from lowercase alphabet
    name_length = 8  # Adjust the length of the random name as needed
    random_name = ''.join(random.choice(string.ascii_lowercase) for _ in range(name_length))
    return random_name
    
# Adjust the path to include the directory containing your project
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_path)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crmapp.settings')
django.setup()

from crmapplication.models import Customer  # Now you can import the model
customers = Customer.objects.all()

for customer in customers:
    if customer.first_name == "":
        name = generate_random_name()
        customer.first_name = name
        print(customer.customer_id ,"---" , name,  " ---updated")
        customer.save()

print("customer  updated successfully.")
