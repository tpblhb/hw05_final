from django import template
from django.forms import Field

register = template.Library()


@register.filter
def addclass(field: Field, css: str) -> str:
    return field.as_widget(
        attrs={
            'class': css,
        },
    )
