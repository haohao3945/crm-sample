import os
import django
import sys
import random
import string
import pandas as pd
import streamlit as st

    
# Adjust the path to include the directory containing your project
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_path)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crmapp.settings')
django.setup()

    
from crmapplication.models import Customer,Invoice  # Now you can import the model
def showrecord(df, name):
    print("Data frame name -------", name)
    print("Data inside : ")
    print(df)
    print("Data describe: ")
    print(df.describe())
    print("Data types")
    print(df.dtypes)

# Retrieve data from Customer model
customers_data = Customer.objects.all().values()
customer_df = pd.DataFrame(customers_data)
customers_data = None
showrecord(customer_df, "Customers data")

# Retrieve data from Invoice model
invoices_data = Invoice.objects.all().values()
invoice_df = pd.DataFrame(invoices_data)
invoices_data = None
showrecord(invoice_df, "Invoice data")


# Please give me today lead




# Please seperate me with unattend leads, on follow up lead, follow up after, close case, give up, 


# Monthly sales



# customer lifetime value analysis
