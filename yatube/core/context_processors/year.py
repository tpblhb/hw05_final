from datetime import date

from django.http import HttpRequest, HttpResponse


def year(request: HttpRequest) -> HttpResponse:
    return {
        'year': date.today().year,
    }
