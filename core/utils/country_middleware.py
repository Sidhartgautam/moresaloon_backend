import requests
from django.conf import settings

class CountryDomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # url = 'https://api.ipify.org/?format=json'

        # response = requests.get(url)

        # if response.status_code == 200:
        #     data = response.json()
        #     ip = data.get('ip')
        # else:
        #     ip = None
        
        # reader = geoip2.database.Reader(f'{settings.GEOIP_PATH}/GeoLite2-City.mmdb')
        # try:
        #     country = reader.city(ip)
        #     country_code = country.country.iso_code
        # except Exception as e:
        #     country_code = 'SE'
        
        request.country_code = 'SE'
        response = self.get_response(request)
        return response
