from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse


def paginate(
    request: HttpRequest,
    queryset: str,
    quantity: int = settings.PAGE_SIZE,
) -> HttpResponse:
    return Paginator(queryset, quantity).get_page(request.GET.get('page'))


def truncatechars(chars: str, trim: int = settings.MAX_DEFAULT_LENGTH) -> str:
    return chars[:trim] + '…' if len(chars) > trim else chars
