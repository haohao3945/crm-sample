from django import forms
from .models import Customer,Invoice

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        
        
        
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = '__all__'