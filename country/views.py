from rest_framework import generics
from .serializers import CountrySerializer
from .models import Country
from core.utils.response import PrepareResponse

# Create your views here.
class CountryListView(generics.GenericAPIView):
    serializer_class = CountrySerializer

    def get(self, request, *args, **kwargs):
        country = Country.objects.all()
        serializer = self.get_serializer(country, many=True)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Country fetched successfully"
        )
        return response.send(200)