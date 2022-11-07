from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse


def paginate(
    request: HttpRequest, queryset: str, quantity: int
) -> HttpResponse:
    return Paginator(queryset, quantity).get_page(request.GET.get('page'))
