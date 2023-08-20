import pandas as pd
import os
import django
from datetime import datetime
import sys
import random
import string

# Adjust the path to include the directory containing your project
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_path)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crmapp.settings')
django.setup()

from crmapplication.models import Invoice, Customer  # Import your models

def generate_random_name():
    # Generate a random name using letters from lowercase alphabet
    name_length = 8  # Adjust the length of the random name as needed
    random_name = ''.join(random.choice(string.ascii_lowercase) for _ in range(name_length))
    return random_name

def import_invoices_from_excel(file_path):
    df = pd.read_csv(file_path)  # Read CSV file

    for index, row in df.iterrows():
        # Convert Excel date format to Django's expected format
        invoice_date_str = row['invoice_date']
        invoice_date = datetime.strptime(invoice_date_str, '%m/%d/%Y %H:%M').strftime('%Y-%m-%d')
        customer_id = row['customerID']

        if pd.notna(customer_id):  # Check if customer_id is not NaN
            customer_id = int(customer_id)  # Convert to integer
            customer, created = Customer.objects.get_or_create(customer_id=customer_id)
        else:
            random_name = generate_random_name()
            customer, created = Customer.objects.get_or_create(first_name=random_name, last_name=random_name)

        invoice = Invoice(
            invoice_date=invoice_date,
            customer=customer,
            country=row['country'],
            quantity=row['quantity'],
            amount=row['amount'].replace(',', '.'),
            # ... other fields
        )
        invoice.save()

if __name__ == "__main__":
    excel_file_path = "crmapplication/customer_relationship.csv"
    import_invoices_from_excel(excel_file_path)
    print("Invoices imported successfully.")
