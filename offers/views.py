from rest_framework.generics import CreateAPIView, ListAPIView
from .models import SaloonOffers, SaloonCoupons
from .serializers import SaloonOfferSerializer, CouponSerializer
from core.utils.response import PrepareResponse  # Assuming you have a utility for consistent responses.

class SaloonOfferCreateView(CreateAPIView):
    serializer_class = SaloonOfferSerializer
    queryset = SaloonOffers.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Saloon offer created successfully"
            )
            return response.send(code=201)
        response = PrepareResponse(
            success=False,
            data=serializer.errors,
            message="Failed to create saloon offer"
        )
        return response.send(code=400)


class SaloonOfferListView(ListAPIView):
    serializer_class = SaloonOfferSerializer
    queryset = SaloonOffers.objects.all()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Saloon offers fetched successfully"
        )
        return response.send(code=200)
    
class CouponCreateView(CreateAPIView):
    serializer_class = CouponSerializer
    queryset = SaloonCoupons.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Coupon created successfully"
            )
            return response.send(code=201)
        response = PrepareResponse(
            success=False,
            data=serializer.errors,
            message="Failed to create coupon"
        )
        return response.send(code=400)
    
class CouponListView(ListAPIView):
    serializer_class = CouponSerializer
    queryset = SaloonCoupons.objects.all()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Coupons fetched successfully"
        )
        return response.send(code=200)

