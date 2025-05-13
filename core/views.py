from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import logout, login
from django.db.models import Q
from .models import User, Customer, Car, Loan, Service, CarTransaction, Report, Department, Employee
from .forms import (
    CustomUserCreationForm, CarForm, LoanApplicationForm,
    ServiceRequestForm, ReportForm, EmployeeForm
)
from django.http import HttpResponseNotAllowed

def is_admin(user):
    return user.is_authenticated and user.role == User.Role.ADMIN

def is_customer(user):
    return user.is_authenticated and user.role == User.Role.CUSTOMER

def is_employee(user):
    return user.is_authenticated and user.role == User.Role.EMPLOYEE

def is_finance(user):
    return user.is_authenticated and user.role == User.Role.FINANCE

# Test view
def test_view(request):
    return render(request, 'test.html', {'message': 'Template test!'})

# Home page
def home_view(request):
    cars = Car.objects.filter(status=Car.Status.AVAILABLE)[:6]  # Show 6 available cars
    return render(request, 'core/home.html', {'cars': cars})

# Authentication views
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})

# Customer views
@login_required
@user_passes_test(is_customer)
def customer_dashboard_view(request):
    customer = request.user.customer
    loans = Loan.objects.filter(customer=customer)
    services = Service.objects.filter(customer=customer)
    transactions = CarTransaction.objects.filter(customer=customer)
    return render(request, 'core/customer/dashboard.html', {
        'loans': loans,
        'services': services,
        'transactions': transactions
    })

@login_required
@user_passes_test(is_customer)
def customer_loans_view(request):
    loans = Loan.objects.filter(customer=request.user.customer)
    return render(request, 'core/customer/loans.html', {'loans': loans})

@login_required
@user_passes_test(is_customer)
def customer_services_view(request):
    services = Service.objects.filter(customer=request.user.customer)
    return render(request, 'core/customer/services.html', {'services': services})

@login_required
@user_passes_test(is_customer)
def customer_transactions_view(request):
    transactions = CarTransaction.objects.filter(customer=request.user.customer)
    return render(request, 'core/customer/transactions.html', {'transactions': transactions})

# Admin views
@login_required
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    total_cars = Car.objects.count()
    total_customers = Customer.objects.count()
    total_employees = Employee.objects.count()
    pending_loans = Loan.objects.filter(status=Loan.Status.PENDING).count()
    pending_services = Service.objects.filter(status=Service.Status.PENDING).count()
    
    return render(request, 'core/admin/dashboard.html', {
        'total_cars': total_cars,
        'total_customers': total_customers,
        'total_employees': total_employees,
        'pending_loans': pending_loans,
        'pending_services': pending_services
    })

@login_required
@user_passes_test(is_admin)
def employee_list_view(request):
    employees = Employee.objects.all()
    return render(request, 'core/admin/employee_list.html', {'employees': employees})

@login_required
@user_passes_test(is_admin)
def employee_add_view(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Role.ADMIN
            user.save()
            messages.success(request, 'Employee added successfully!')
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'core/admin/employee_form.html', {'form': form})

# Car views
def car_list_view(request):
    cars = Car.objects.filter(status=Car.Status.AVAILABLE)
    return render(request, 'core/cars/list.html', {'cars': cars})

def car_detail_view(request, pk):
    car = get_object_or_404(Car, pk=pk)
    return render(request, 'core/cars/detail.html', {'car': car})

@login_required
@user_passes_test(is_customer)
def car_buy_view(request, pk):
    car = get_object_or_404(Car, pk=pk, status=Car.Status.AVAILABLE)
    if request.method == 'POST':
        transaction = CarTransaction.objects.create(
            car=car,
            customer=request.user.customer,
            transaction_type=CarTransaction.TransactionType.PURCHASE,
            amount=car.price
        )
        car.status = Car.Status.SOLD
        car.save()
        messages.success(request, 'Car purchased successfully!')
        return redirect('customer_transactions')
    return render(request, 'core/cars/buy.html', {'car': car})

# Loan views
@login_required
@user_passes_test(is_customer)
def loan_apply_view(request):
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.customer = request.user.customer
            loan.save()
            messages.success(request, 'Loan application submitted successfully!')
            return redirect('customer_loans')
    else:
        form = LoanApplicationForm()
    return render(request, 'core/loans/apply.html', {'form': form})

@login_required
def loan_detail_view(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    if not (request.user.role == User.Role.ADMIN or loan.customer == request.user.customer):
        messages.error(request, 'You do not have permission to view this loan.')
        return redirect('home')
    return render(request, 'core/loans/detail.html', {'loan': loan})

# Service views
@login_required
@user_passes_test(is_customer)
def service_request_view(request):
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.customer = request.user.customer
            service.save()
            messages.success(request, 'Service request submitted successfully!')
            return redirect('customer_services')
    else:
        form = ServiceRequestForm()
    return render(request, 'core/services/request.html', {'form': form})

@login_required
def service_detail_view(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if not (request.user.role == User.Role.ADMIN or request.user.role == User.Role.SERVICES or service.customer == request.user.customer):
        messages.error(request, 'You do not have permission to view this service.')
        return redirect('home')
    
    # Handle service status updates
    if request.method == 'POST' and (request.user.role == User.Role.ADMIN or request.user.role == User.Role.SERVICES):
        action = request.POST.get('action')
        if action == 'start' and service.status == Service.Status.PENDING:
            service.status = Service.Status.IN_PROGRESS
            messages.success(request, 'Service has been started.')
        elif action == 'complete' and service.status == Service.Status.IN_PROGRESS:
            service.status = Service.Status.COMPLETED
            messages.success(request, 'Service has been completed.')
        service.save()
        return redirect('service_detail', pk=pk)
    
    return render(request, 'core/services/detail.html', {'service': service})

@login_required
def car_service_view(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.car = car
            service_request.customer = request.user.customer
            
            # Set default cost if not provided
            if not service_request.cost:
                # Default costs based on service type
                default_costs = {
                    'MAINTENANCE': 150.00,
                    'REPAIR': 300.00,
                    'INSPECTION': 75.00,
                    'BODYWORK': 500.00,
                    'DETAILING': 200.00,
                }
                service_request.cost = default_costs.get(service_request.service_type, 100.00)
            
            service_request.save()
            messages.success(request, 'Service request submitted successfully!')
            return redirect('car_detail', pk=pk)
    else:
        form = ServiceRequestForm()
    
    return render(request, 'core/services/service_request.html', {
        'car': car,
        'form': form
    })

# Report views
@login_required
@user_passes_test(is_admin)
def report_list_view(request):
    reports = Report.objects.all()
    return render(request, 'core/admin/report_list.html', {'reports': reports})

@login_required
@user_passes_test(is_admin)
def report_create_view(request):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user
            report.save()
            messages.success(request, 'Report created successfully!')
            return redirect('report_list')
    else:
        form = ReportForm()
    return render(request, 'core/admin/report_form.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

def cart_view(request):
    return render(request, 'core/cart.html')

def role_dashboard_redirect(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role == User.Role.CUSTOMER:
        return redirect('customer_dashboard')
    elif request.user.role == User.Role.FINANCE:
        return redirect('finance_dashboard')
    elif request.user.role == User.Role.SERVICES:
        return redirect('services_dashboard')
    elif request.user.role == User.Role.SALES:
        return redirect('sales_dashboard')
    elif request.user.role == User.Role.ADMIN:
        return redirect('admin_dashboard')
    else:
        return redirect('home')

@login_required
def finance_dashboard(request):
    if not request.user.role == User.Role.FINANCE:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    # Get reports for the finance department
    department = Department.objects.get(name=Department.Name.FINANCE)
    reports = Report.objects.filter(
        Q(department=department) | Q(type=Report.ReportType.FINANCE)
    ).order_by('-created_at')
    
    return render(request, 'core/finance/dashboard.html', {
        'reports': reports
    })

@login_required
def services_dashboard(request):
    # Example schema/data for services
    reports = Report.objects.filter(department__name=Department.Name.SERVICES)
    return render(request, 'core/services/dashboard.html', {'reports': reports})

@login_required
def sales_dashboard(request):
    # Example schema/data for sales
    reports = Report.objects.filter(department__name=Department.Name.SALES)
    return render(request, 'core/sales/dashboard.html', {'reports': reports})

@login_required
@user_passes_test(is_finance)
def employee_report_create_view(request):
    if request.method == 'POST':
        try:
            department = Department.objects.get(name=Department.Name.FINANCE)
            report = Report.objects.create(
                title=request.POST.get('title'),
                type=request.POST.get('type'),
                content=request.POST.get('content'),
                created_by=request.user,
                department=department
            )
            messages.success(request, 'Report submitted successfully! An admin will review it shortly.')
            return redirect('finance_dashboard')
        except Exception as e:
            messages.error(request, f'Error creating report: {str(e)}')
            return redirect('employee_report_create')
    
    return render(request, 'core/finance/report_create.html') 