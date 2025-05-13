from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError, InvalidOperation):
        return 0

@register.filter
def divide(value, arg):
    try:
        if arg and Decimal(str(arg)) != 0:
            return Decimal(str(value)) / Decimal(str(arg))
        return 0
    except (ValueError, TypeError, InvalidOperation):
        return 0

@register.filter
def percentage(value):
    try:
        return "{:.2f}%".format(float(value))
    except (ValueError, TypeError):
        return "0.00%"

@register.filter
def currency(value):
    try:
        return "${:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return "$0.00" 