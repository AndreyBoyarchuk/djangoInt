from django import template

register = template.Library()

@register.filter
def sum_values(value, arg):
    return sum(float(item[arg]) for item in value)

@register.filter
def subtract(value, arg):
    return float(value) - float(arg)

@register.filter
def add(value, arg):
    return float(value) + float(arg)
