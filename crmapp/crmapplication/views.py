import os
import django
from io import BytesIO
import base64
import sys
import random
import string
from django.core.paginator import Paginator, Page
from django.shortcuts import render,get_object_or_404,redirect
from .forms import CustomerForm,InvoiceForm  
from .models import Customer,Invoice
from django.db.models import Q
import re
from datetime import datetime, timedelta
import pandas as pd
import json
from .analytics_test import analyze_data


def validate_date(date_string):
    formats = [
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d %b %Y",
        "%d.%m.%Y",
        "%m.%d.%Y"
    ]
    
    for format_str in formats:
        try:
            date_obj = datetime.strptime(date_string, format_str)
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            pass
    
    return None

def contact_list(request):
    contacts = Customer.objects.all()
    # display by ascending order
    contacts = contacts.order_by('first_name')
    paginator = Paginator(contacts, 10)  # Show 10 contacts per page
    page = request.GET.get('page')
    contacts = paginator.get_page(page)

    return render(request, 'crm/contact_list.html', {'contacts': contacts})


def contact_search(request):
    query = request.GET.get('q')
    if query:
        # Exclude certain values based on the query
        if query == 'unattend':
            contacts = Customer.objects.all().exclude(
                Q(progress__contains='give') |
                Q(progress__contains='follow') |
                Q(progress__contains='close')
            )
            
        else:
            base_contacts = Customer.objects.filter(
                Q(customer_id__contains=query) |
                Q(first_name__contains=query) |
                Q(last_name__contains=query) |
                Q(email__contains=query) |
                Q(phone__contains=query) |
                Q(progress__contains=query) |
                Q(address__contains=query)
            )
        
            contacts = base_contacts
    else:
        contacts = Customer.objects.all()

    # Display by ascending order
    contacts = contacts.order_by('first_name')
    return render(request, 'crm/contact_list.html', {'contacts': contacts})

def change_id_to_name(df):
    # Fetch customer names based on customer IDs
    customer_ids = df['customer_id'].unique()
    customer_names = {customer.customer_id: f"{customer.first_name} {customer.last_name}" for customer in Customer.objects.filter(customer_id__in=customer_ids)}

    # Create a new column 'customer_name' and map customer IDs to names
    df['customer_name'] = df['customer_id'].map(customer_names)

    return df
    

def dashboard(request):
    # initialize the data
    customer_df = pd.DataFrame(Customer.objects.all().values())
    invoice_df = pd.DataFrame(Invoice.objects.all().values())

    # remove all negative value in invoice 
    # Identify return and discount transactions
    return_mask = (invoice_df['amount'] < 0) & (-invoice_df['amount'].isin(invoice_df['amount'].abs()))
    discount_mask = (invoice_df['amount'] < 0) & (~return_mask)

    # Get customer and date information for return and discount transactions
    return_customers_dates = invoice_df.loc[return_mask, ['customer_id', 'invoice_date']]
    discount_customers_dates = invoice_df.loc[discount_mask, ['customer_id', 'invoice_date']]


    # Remove return transactions
    invoice_df = invoice_df[~invoice_df.index.isin(return_customers_dates.index)]

    # Remove discount transactions (only negative amounts)
    invoice_df = invoice_df[~invoice_df.index.isin(discount_customers_dates.index)]

    # Convert 'invoice_date' column to datetime if it's not already
    invoice_df['invoice_date'] = pd.to_datetime(invoice_df['invoice_date'])

    # Filter rows where 'invoice_date' is '9 Dec 2021'
    filtered_invoices = invoice_df[invoice_df['invoice_date'] == '2021-12-9']

    # Count the number of occurrences
    count = filtered_invoices.shape[0]



    # Monthly sales graph 
    end_date = datetime(2021, 12, 9)
    start_date = end_date - timedelta(days=30)
    filtered_df = invoice_df[(invoice_df['invoice_date'] >= start_date) & (invoice_df['invoice_date'] <= end_date)]
    #print (filtered_df)

    # Sum the amounts on each date
    sales_summary = filtered_df.groupby('invoice_date')['amount'].sum().reset_index()
    
    # Convert Decimal values to float for serialization
    sales_summary['amount'] = sales_summary['amount'].astype(float)
    # Prepare data for graph
    graph_data = json.dumps({
        'labels': sales_summary['invoice_date'].dt.strftime('%Y-%m-%d').tolist(),
        'data': sales_summary['amount'].tolist(),
    })
    
    # Track progress part
    # Total count of customers
    total_count = len(customer_df)

    # Define keywords
    unattend = 0
    followup = 0
    after = 0
    close_case = 0
    give_up = 0

    # Count occurrences of keywords
    for i in range(total_count):
        progress = customer_df.loc[i, 'progress']  # Get the 'progress' value at index i
        if progress == 'give_up' or 'npu' in progress:
            give_up += 1
        elif progress == 'close_case':
            close_case += 1
        elif 'after' in progress or progress == 'Follow-up After':
            after += 1
        elif 'follow up' in progress or progress == 'follow_up':
            followup += 1
        else:
            unattend += 1

    # Create a list with results
    results = [
        ('Unattend Leads', unattend),
        ('Following Up Leads', followup),
        ('Follow Up After Leads', after),
        ('Closed Case Customer', close_case),
        ('Give Up Leads', give_up),
    ]
    
    predict_data = analyze_data()
    # Convert the dictionaries to DataFrames
    hot_lead = pd.DataFrame(predict_data['hot_clv']).astype(int)
    cold_lead = pd.DataFrame(predict_data['cold_clv']).astype(int)
    high_ticket_lead = pd.DataFrame(predict_data['high_ticket']).astype(int)
    one_buyer_lead = pd.DataFrame(predict_data['one_buyer']).astype(int)

    # Apply the change_id_to_name function to each DataFrame
    hot_lead = change_id_to_name(hot_lead)
    cold_lead = change_id_to_name(cold_lead)
    high_ticket_lead = change_id_to_name(high_ticket_lead)
    one_buyer_lead = change_id_to_name(one_buyer_lead)

    hot_lead_count = len(hot_lead)
    cold_lead_count = len(cold_lead)
    high_ticket_count = len(high_ticket_lead)
    one_time_count = len(one_buyer_lead)
    
    print(hot_lead,flush=True)
    #print(dataframe_to_html_table(hot_lead))
    context = {
        'lead_count': count,
        'graph_data': graph_data,
        'tracking_count':results,
        'one_time_buyer_percentage' :one_time_count,
        'hot_lead_count' : hot_lead_count,
        'cold_lead_count' : cold_lead_count,
        'high_ticket_count':high_ticket_count,
        "hot_lead": hot_lead.to_dict(orient='records'),
        "cold_lead": cold_lead.to_dict(orient='records'),
        "high_ticket_lead": high_ticket_lead.to_dict(orient='records'),
        "one_buyer_lead": one_buyer_lead.to_dict(orient='records'),
    }
    
    
    # Convert the results to a Pandas DataFrame
    results_df = pd.DataFrame(results)
    return render(request, 'crm/dashboard.html',{'context': context})

def order_data(request):
    order = Invoice.objects.all()
    # Order the results in descending order by invoice_date
    order = order.order_by('-invoice_date')
    paginator = Paginator(order, 10)  # Show 10 order per page
    page = request.GET.get('page')
    order = paginator.get_page(page)
    return render(request, 'crm/order_data.html',{'orders':order})

MONTH_MAP = {
    'jan': '01',
    'feb': '02',
    'mar': '03',
    'apr': '04',
    'may': '05',
    'jun': '06',
    'jul': '07',
    'aug': '08',
    'sep': '09',
    'sept': '09',
    'oct': '10',
    'nov': '11',
    'dec': '12',
}

def normalize_query(query):
    # Normalize month search query to numeric format if it's an English month name
    normalized_query = query.lower()
    if normalized_query in MONTH_MAP:
        return MONTH_MAP[normalized_query]
    return None
    
def order_search(request):
    query = request.GET.get('q')

    if query:
        normalized_query = normalize_query(query)
        
        if 'clv' in query:  # Check if 'clv' is present in the query
            # Clear 'clv' from the query and search only by customer_id
            customer_id_query = query.replace('clv', '').strip()
            order = Invoice.objects.filter(customer_id=customer_id_query)
        elif normalized_query in MONTH_MAP.values():         
            # Search for invoices by month
            order = Invoice.objects.filter(invoice_date__month=normalized_query)
        elif validate_date(query):
            # If it is date, then search by date
            order = Invoice.objects.filter(invoice_date=validate_date(query))
        else:
            # Perform the regular search
            order = Invoice.objects.filter(
                Q(invoice_id__contains=query) |
                Q(invoice_date__icontains=query) |
                Q(customer__first_name__exact=query) |
                Q(customer__last_name__exact=query) |
                Q(country__contains=query) |
                Q(notice_to_consider__contains=query)
            )
    
    
    # Order the results in descending order by invoice_date
    order = order.order_by('-invoice_date')
    
    return render(request, 'crm/order_data.html', {'orders': order})

# Function to handle create, update and delete of the customer
def customer_detail(request):
    customer_id = request.GET.get('id')
    customer = None
    form = None
    
    if customer_id: # If the customer id exist , note that there is no type input at id, so no handling error
        customer = get_object_or_404(Customer, pk=customer_id) # If no id, then get 404 error
        form = CustomerForm(instance=customer)
        if request.method == 'POST':  # if there are any input
            if 'delete' in request.POST: # if delete button click
                customer.delete()
                return redirect('contact_list')
            else:
                form = CustomerForm(request.POST, instance=customer) # if there is any update
                if form.is_valid():
                    form.save()
                    customer_id = None  # Clear customer_id after editing
    else:
        if request.method == 'POST':   # If user add input
            form = CustomerForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('contact_list')
        else:
            form = CustomerForm()   # If non of above then display empty form
            
    context = {
        'customer': customer,
        'form': form
    }
    
    return render(request, 'crm/customer_detail.html', context)
    
# Function to handle create, update and delete of the invoice
def order_detail(request):
    order_id = request.GET.get('id')
    order = None
    form = None
    if order_id:  # If the invoice id exist , note that there is no type input at id, so no handling error
        order = get_object_or_404(Invoice, pk=order_id)  
        form = InvoiceForm(instance=order)
        if request.method == 'POST':  
            if 'delete' in request.POST: # if delete button click
                order.delete()
                return redirect('order_data')
            else:
                form = InvoiceForm(request.POST, instance=order)# if there is any update
                if form.is_valid():
                    form.save()
                    order_id = None  # Clear order_id after editing
    else:
        if request.method == 'POST':          # If user add input
            form = InvoiceForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('order_data')
        else:
            form = InvoiceForm()     # If non of above then display empty form
            
    context = {
        'order': order,
        'form': form
    }
    
    return render(request, 'crm/order_detail.html', context)