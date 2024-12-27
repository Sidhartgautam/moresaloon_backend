from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.views import APIView
from .models import SaloonOffers, SaloonCoupons, CouponUsage
from .serializers import SaloonOfferSerializer, CouponSerializer,CouponListSerializer
from core.utils.response import PrepareResponse  # Assuming you have a utility for consistent responses.
from rest_framework.permissions import IsAuthenticated


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
    serializer_class = CouponListSerializer

    def get_queryset(self):
        saloon_id = self.kwargs.get('saloon_id')  # Extract saloon_id from the URL
        country_code = self.request.headers.get('Country-Code')  # Extract country code from headers

        if not saloon_id:
            return PrepareResponse(
                success=False,
                message="Saloon ID is required."
            ).send(
                code=400
            )

        queryset = SaloonCoupons.objects.filter(saloon_id=saloon_id).prefetch_related('services')

        if country_code:
            queryset = queryset.filter(saloon__country__code=country_code)

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Coupons fetched successfully"
        )
        return response.send(code=200)
    
class CheckCouponValidityAPIView(APIView):
    """
    API View to check the validity of a coupon for a specific saloon.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        coupon_code = request.query_params.get('coupon_code', None)
        saloon_id = request.query_params.get('saloon_id', None)

        if not coupon_code or not saloon_id:
            return PrepareResponse(
                success=False,
                message="Both coupon_code and saloon_id are required."
            ).send(400)

        try:
            coupon = SaloonCoupons.objects.get(code=coupon_code, saloon_id=saloon_id)

            if not coupon.is_active():
                return PrepareResponse(
                    success=False,
                    message="Coupon is expired."
                ).send(400)

            # Check if the user has already used this coupon
            user = request.user
            if CouponUsage.objects.filter(coupon=coupon, user=user).exists():
                return PrepareResponse(
                    success=False,
                    message="You have already used this coupon."
                ).send(400)

            discount = coupon.percentage_discount or coupon.fixed_discount
            discount_type = "percentage" if coupon.percentage_discount else "fixed"

            return PrepareResponse(
                success=True,
                message="Coupon is valid.",
                data={
                    "coupon_code": coupon.code,
                    "discount": discount,
                    "discount_type": discount_type,
                    "start_date": coupon.start_date,
                    "end_date": coupon.end_date,
                }
            ).send(200)
        except SaloonCoupons.DoesNotExist:
            return PrepareResponse(
                success=False,
                message="Invalid coupon code or saloon ID."
            ).send(404)

