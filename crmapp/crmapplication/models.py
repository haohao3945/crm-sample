from django.db import models

# Create your models here.
class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length = 255,blank=True)
    last_name = models.CharField(max_length = 255, blank=True)
    email = models.EmailField( blank=True)
    phone = models.CharField(max_length=20,blank = True)
    progress = models.CharField(max_length = 255,blank=True)
    address = models.TextField(blank = True)
    
    def __str__(self):
        return f"{self.first_name}{self.last_name}"
        
        
        
class Invoice(models.Model):
    invoice_id = models.AutoField(primary_key=True)
    invoice_date = models.DateField( blank=True)
    invoice_number = models.CharField(max_length=50, blank=True)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.DO_NOTHING)
    country = models.CharField(max_length=50, blank=True)
    quantity = models.IntegerField( blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    notice_to_consider = models.CharField(max_length = 255,blank=True)
    

    def __str__(self):
        return f"Invoice #{self.invoice_id} - {self.customer}"
