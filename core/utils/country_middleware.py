import requests
from django.conf import settings

class CountryDomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        country_code = request.headers.get('X-Country-Code')
        request.country_code = country_code
        response = self.get_response(request)
        return response