from django import template
from django.template.defaultfilters import stringfilter


register = template.Library()


@register.filter
@stringfilter
def uncapitalize(value):
    if value is None or len(value) == 0:
        return value

    return value[0].lower() + value[1:]
