from django.core.paginator import Paginator, Page
from django.shortcuts import render,get_object_or_404,redirect
from .forms import CustomerForm,InvoiceForm  
from .models import Customer,Invoice
from django.db.models import Q
import re
from datetime import datetime

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
    paginator = Paginator(contacts, 10)  # Show 10 contacts per page
    page = request.GET.get('page')
    contacts = paginator.get_page(page)
    
    return render(request, 'crm/contact_list.html', {'contacts': contacts})


def contact_search(request):
    query = request.GET.get('q')
    if query:
        contacts = Customer.objects.filter(
            Q(customer_id__contains=query) | Q(first_name__contains=query) | Q(last_name__contains=query) | Q(email__contains=query) | Q(phone__contains=query) | Q(progress__contains=query)| Q(address__contains=query)
        )
    else:
        contacts = Customer.objects.all()
    return render(request, 'crm/contact_list.html', {'contacts': contacts})


def dashboard(request):
    return render(request, 'crm/dashboard.html')

def order_data(request):
    order = Invoice.objects.all()
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
        
        if normalized_query in MONTH_MAP.values():         
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