from django.shortcuts import render
from .models import Contact

def contact_list(request):
    contacts = Contact.objects.all()
    return render(request, 'crm/contact_list.html', {'contacts': contacts})

def dashboard(request):
    return render(request, 'crm/dashboard.html')
