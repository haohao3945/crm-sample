from django.urls import path
from . import views

urlpatterns = [
    path('contacts/', views.contact_list, name='contact_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('order_data/', views.order_data, name='order_data'),
    path('customer_detail/', views.customer_detail, name='customer_detail'),
]
