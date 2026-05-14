import threading
from django.db import ProgrammingError, OperationalError
from django.shortcuts import render

_thread_locals = threading.local()

def get_current_request():
    return getattr(_thread_locals, 'request', None)

class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, (ProgrammingError, OperationalError)):
            if 'does not exist' in str(exception) or 'no such table' in str(exception).lower():
                return render(request, 'analytics/error.html', {
                    'message': 'The database is currently being initialized or updated. Please run migrations or wait a moment.',
                    'title': 'Database Error'
                }, status=503)
        return None

def get_client_ip():
    request = get_current_request()
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    return None
