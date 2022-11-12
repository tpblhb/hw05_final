from django import template
from django.forms import Field
from django.utils.safestring import SafeText

register = template.Library()


@register.filter
def addclass(field: Field, css: SafeText) -> SafeText:
    return field.as_widget(
        attrs={
            'class': css,
        },
    )
