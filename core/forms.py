from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Customer, Car, Loan, Service, Report, Department, Employee
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.Role.choices, label='Register as')
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False, help_text='Select department if registering as Employee')
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'address', 'role', 'department')
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
            # Create associated customer profile if role is CUSTOMER
            if user.role == User.Role.CUSTOMER:
                Customer.objects.get_or_create(user=user)
            # Create employee profile if role is EMPLOYEE
            if user.role == User.Role.EMPLOYEE and self.cleaned_data['department']:
                Employee.objects.create(user=user, department=self.cleaned_data['department'], position='Employee', hire_date=None, salary=0)
        return user

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['make', 'model', 'year', 'price', 'mileage', 'condition']

class LoanApplicationForm(forms.ModelForm):
    amount = forms.DecimalField(
        min_value=1000,
        max_value=1000000,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter loan amount',
            'min': '1000',
            'max': '1000000',
            'step': '100'
        }),
        help_text='Loan amount must be between $1,000 and $1,000,000'
    )
    
    interest_rate = forms.DecimalField(
        min_value=0.1,
        max_value=30.0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter interest rate',
            'min': '0.1',
            'max': '30.0',
            'step': '0.1'
        }),
        help_text='Interest rate must be between 0.1% and 30%'
    )
    
    term_months = forms.IntegerField(
        min_value=12,
        max_value=84,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter loan term in months',
            'min': '12',
            'max': '84'
        }),
        help_text='Loan term must be between 12 and 84 months'
    )
    
    car = forms.ModelChoiceField(
        queryset=Car.objects.filter(status='AVAILABLE'),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text='Select an available car for the loan'
    )

    class Meta:
        model = Loan
        fields = ['car', 'amount', 'interest_rate', 'term_months']

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        car = cleaned_data.get('car')
        
        if amount and car and amount > car.price:
            raise forms.ValidationError(
                "Loan amount cannot exceed the car's price of ${:,.2f}".format(car.price)
            )
        
        return cleaned_data

class ServiceRequestForm(forms.ModelForm):
    SERVICE_TYPES = [
        ('MAINTENANCE', 'Regular Maintenance'),
        ('REPAIR', 'Repair'),
        ('INSPECTION', 'Inspection'),
        ('BODYWORK', 'Body Work'),
        ('DETAILING', 'Detailing'),
    ]

    service_type = forms.ChoiceField(
        choices=SERVICE_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Select service type'
        }),
        help_text='Choose the type of service needed'
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Describe the service needed',
            'rows': 4,
            'style': 'resize: vertical;'
        }),
        help_text='Provide detailed description of the service needed'
    )
    
    car = forms.ModelChoiceField(
        queryset=Car.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text='Select the car for service'
    )
    
    preferred_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text='Select your preferred service date',
        required=False
    )
    
    urgent = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Check if this is an urgent service request'
    )

    cost = forms.DecimalField(
        min_value=0,
        max_value=100000,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Service cost',
            'min': '0',
            'step': '0.01'
        }),
        help_text='Service cost will be determined by our team'
    )

    class Meta:
        model = Service
        fields = ['car', 'service_type', 'description', 'preferred_date', 'urgent', 'cost']

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) < 20:
            raise forms.ValidationError(
                "Please provide a more detailed description (at least 20 characters)"
            )
        return description

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['type', 'title', 'content', 'department']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 6}),
        }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'address']
        widgets = {
            'password': forms.PasswordInput(),
        } 