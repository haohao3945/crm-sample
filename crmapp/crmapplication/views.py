from django.core.paginator import Paginator, Page
from django.shortcuts import render
#from .forms import CustomerForm  # Import your customer form
from .models import Customer,Invoice
from django.db.models import Q


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
    
def customer_detail(request):
    print("Request - ", request)
 #   if request.method == 'POST':
 #       form = CustomerForm(request.POST)
    
 #   if form.is_valid():
  #      form.save()
  #      return redirect('customer_detail')
  #  else:
  #      form = CustomerForm()
    
   # context = {'form': form, 'add_customer': True}
    #return render(request, 'customer_detail.html', context)
    return render(request, 'crm/customer_detail.html')