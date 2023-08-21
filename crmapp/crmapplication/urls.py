from django.urls import path
from . import views

urlpatterns = [
    path('contacts/', views.contact_list, name='contact_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('order_data/', views.order_data, name='order_data'),
    path('order_detail/', views.order_detail, name='order_detail'),
    path('order_detail/<str:action>/', views.order_detail, name='order_detail'),
    path('customer_detail/', views.customer_detail, name='customer_detail'),
    path('customer_detail/<str:action>/', views.customer_detail, name='customer_detail'),
    path('contact_search/', views.contact_search, name='contact_search'),
    path('order_search/', views.order_search, name='order_search'),

]
