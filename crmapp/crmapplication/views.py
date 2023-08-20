from django.core.paginator import Paginator, Page
from django.shortcuts import render
#from .forms import CustomerForm  # Import your customer form
from .models import Customer,Invoice

def contact_list(request):
    contacts = Customer.objects.all()
    paginator = Paginator(contacts, 10)  # Show 10 contacts per page
    page = request.GET.get('page')
    contacts = paginator.get_page(page)
    
    return render(request, 'crm/contact_list.html', {'contacts': contacts})

def dashboard(request):
    return render(request, 'crm/dashboard.html')

def order_data(request):
    return render(request, 'crm/order_data.html')
    
def customer_detail(request):
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