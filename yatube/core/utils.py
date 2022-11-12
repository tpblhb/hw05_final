from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse

from yatube.settings import MAX_DEFAULT_LENGTH


def paginate(
    request: HttpRequest,
    queryset: str,
    quantity: int = 10,
) -> HttpResponse:
    return Paginator(queryset, quantity).get_page(request.GET.get('page'))


def truncatechars(chars: str, trim: int = MAX_DEFAULT_LENGTH) -> str:
    return chars[:trim] + '…' if len(chars) > trim else chars
