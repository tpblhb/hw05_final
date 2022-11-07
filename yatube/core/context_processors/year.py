from datetime import datetime

from django.http import HttpRequest, HttpResponse


def year(request: HttpRequest) -> HttpResponse:
    now = (datetime.now()).strftime('%Y')
    return {
        'year': now,
    }
