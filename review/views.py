from rest_framework import generics, permissions
from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer
from saloons.models import Saloon
from rest_framework.exceptions import ValidationError
from core.utils.response import PrepareResponse
from core.utils.pagination import CustomPageNumberPagination
from rest_framework.decorators import permission_classes

class ReviewListView(generics.GenericAPIView):
    serializer_class = ReviewSerializer
    pagination_class = CustomPageNumberPagination
    
    def get(self, request, *args, **kwargs):
        
        saloon_id = self.kwargs['saloon_id']
        review = Review.objects.filter(saloon_id=saloon_id).order_by('-created_at')
        paginator = self.pagination_class()
        queryset = paginator.paginate_queryset(review, request)
        serializer = self.serializer_class(queryset, many=True)
        paginated_data = paginator.get_paginated_response(serializer.data)
        result = paginated_data['results']
        del paginated_data['results']
        response = PrepareResponse(
            success=True,
            message="Saloons Reviews List",
            data=result, meta=paginated_data,
        )
        return response.send(code=200)

    
class UserReviewListView(generics.GenericAPIView):
    serializer_class = ReviewSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user_id=request.user if request.user.is_authenticated else None
        review = Review.objects.filter(user_id=user_id).order_by('-created_at')
        paginator = self.pagination_class()
        queryset = paginator.paginate_queryset(review, request)
        serializer = self.serializer_class(queryset, many=True)
        paginated_data = paginator.get_paginated_response(serializer.data)
        result = paginated_data['results']
        del paginated_data['results']
        response = PrepareResponse(
            success=True,
            message="User Reviews List",
            data=result, meta=paginated_data,
        )
        return response.send(code=200)

class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewCreateSerializer

    @permission_classes([permissions.IsAuthenticated])
    def post(self, request, *args, **kwargs):
        saloon_id = self.kwargs['saloon_id']
        saloon = Saloon.objects.get(id=saloon_id)
        if Review.objects.filter(saloon=saloon, user=request.user if request.user.is_authenticated else None).exists():
            raise ValidationError("You have already reviewed this saloon.")
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=self.request.user, saloon=saloon)
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message='Review created successfully'
            )
            return response.send(201)
        response = PrepareResponse(
            success=False,
            errors=serializer.errors,
            message='Error creating review'
        )
        return response.send(400)


class ReviewRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        saloon_id = self.kwargs['saloon_id']
        review_id = self.kwargs.get('review_id')
        review = Review.objects.get(id=review_id, saloon_id=saloon_id)

        if review.user != self.request.user:
            raise ValidationError("You do not have permission to access this review.")
        
        return review

    def create(self, request, *args, **kwargs):
        saloon_id = self.kwargs['saloon_id']
        saloon = Saloon.objects.get(id=saloon_id)
        
        if Review.objects.filter(saloon=saloon, user=request.user if request.user.is_authenticated else None).exists():
            raise ValidationError("You have already reviewed this saloon.")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user, saloon=saloon)
        
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message='Review created successfully'
        )
        return response.send(201)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message='Review updated successfully'
        )
        return response.send(200)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()

        response = PrepareResponse(
            success=True,
            message='Review deleted successfully'
        )
        return response.send(204)
