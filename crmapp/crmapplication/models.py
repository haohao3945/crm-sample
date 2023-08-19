from django.db import models

# Create your models here.
class Contact(models.Model):
    first_name = models.CharField(max_length = 255)
    last_name = models.CharField(max_length = 255)
    email = models.EmailField()
    phone = models.CharField(max_length=20,blank = True)
    address = models.TextField(blank = True)
    
    def __str__(self):
        return f"{self.first_name}{self.last_name}"