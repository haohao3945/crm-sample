from django import forms
from .models import Customer,Invoice

class CustomerForm(forms.ModelForm):
    class Meta:
        INVOICE_PROGRESS_CHOICES = (
            ('unattended', 'Unattended Leads'),
            ('follow_up', 'On Follow-up Lead'),
            ('follow_up_after', 'Follow-up After'),
            ('close_case', 'Close Case'),
            ('give_up', 'Give Up'),
        )
        model = Customer
        fields = '__all__'
        widgets = {
            'progress': forms.Select(choices=INVOICE_PROGRESS_CHOICES),
            
        }

        
        
        
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = '__all__'
        widgets = {
            'invoice_date': forms.DateInput(attrs={'type': 'date'}),    
        }

