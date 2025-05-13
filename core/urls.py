from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home page
    path('', views.role_dashboard_redirect, name='home'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Customer URLs
    path('customer/dashboard/', views.customer_dashboard_view, name='customer_dashboard'),
    path('customer/loans/', views.customer_loans_view, name='customer_loans'),
    path('customer/services/', views.customer_services_view, name='customer_services'),
    path('customer/transactions/', views.customer_transactions_view, name='customer_transactions'),
    
    # Role dashboards
    path('finance/dashboard/', views.finance_dashboard, name='finance_dashboard'),
    path('services/dashboard/', views.services_dashboard, name='services_dashboard'),
    path('sales/dashboard/', views.sales_dashboard, name='sales_dashboard'),
    
    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin/employees/', views.employee_list_view, name='employee_list'),
    path('admin/employees/add/', views.employee_add_view, name='employee_add'),
    path('admin/reports/', views.report_list_view, name='report_list'),
    path('admin/reports/create/', views.report_create_view, name='report_create'),
    
    # Car URLs
    path('cars/', views.car_list_view, name='car_list'),
    path('cars/<int:pk>/', views.car_detail_view, name='car_detail'),
    path('cars/<int:pk>/buy/', views.car_buy_view, name='car_buy'),
    path('cars/<int:pk>/service/', views.car_service_view, name='car_service'),
    
    # Loan URLs
    path('loans/apply/', views.loan_apply_view, name='loan_apply'),
    path('loans/<int:pk>/', views.loan_detail_view, name='loan_detail'),
    
    # Service URLs
    path('services/request/', views.service_request_view, name='service_request'),
    path('services/<int:pk>/', views.service_detail_view, name='service_detail'),
    
    # Cart URLs
    path('cart/', views.cart_view, name='cart'),
    
    # Employee URLs
    path('employee/report/create/', views.employee_report_create_view, name='employee_report_create'),
] 