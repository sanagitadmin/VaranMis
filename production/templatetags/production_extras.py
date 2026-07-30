from decimal import Decimal

from django import template


register = template.Library()


@register.filter
def smart_number(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float, Decimal)):
        return f"{value:,.2f}".rstrip("0").rstrip(".")
    return value
