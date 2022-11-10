from datetime import datetime

from django.http import HttpRequest, HttpResponse


def year(request: HttpRequest) -> HttpResponse:
    return {
        'year': datetime.now().strftime('%Y'),
    }
