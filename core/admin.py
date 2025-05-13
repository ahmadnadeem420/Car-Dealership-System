from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Department, Employee, Customer, Car,
    Loan, Service, CarTransaction, Report
)
from django.utils.html import format_html

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number', 'address')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number', 'address')}),
    )

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'position', 'hire_date', 'is_active')
    list_filter = ('department', 'is_active', 'hire_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'position')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'credit_score', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'year', 'price', 'status', 'created_at', 'image_tag')
    list_filter = ('status', 'make', 'year')
    search_fields = ('make', 'model', 'year')
    readonly_fields = ('image_tag',)

    def image_tag(self, obj):
        if hasattr(obj, 'image_url') and obj.image_url:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.image_url)
        return ""
    image_tag.short_description = 'Image'

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('customer', 'car', 'amount', 'interest_rate', 'term_months', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__user__username', 'car__make', 'car__model')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('car', 'customer', 'service_type', 'cost', 'status', 'created_at')
    list_filter = ('status', 'service_type', 'created_at')
    search_fields = ('car__make', 'car__model', 'customer__user__username', 'service_type')

@admin.register(CarTransaction)
class CarTransactionAdmin(admin.ModelAdmin):
    list_display = ('car', 'customer', 'transaction_type', 'amount', 'transaction_date')
    list_filter = ('transaction_type', 'transaction_date')
    search_fields = ('car__make', 'car__model', 'customer__user__username')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('type', 'title', 'created_by', 'department', 'created_at')
    list_filter = ('type', 'department', 'created_at')
    search_fields = ('title', 'content', 'created_by__username')

# Register the custom User model
admin.site.register(User, CustomUserAdmin) 