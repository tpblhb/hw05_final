from django import template

register = template.Library()


@register.filter
def addclass(field: str, css: str) -> dict:
    return field.as_widget(
        attrs={
            'class': css,
        },
    )
