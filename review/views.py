from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Review
from .serializers import ReviewSerializer
from saloons.models import Saloon
from rest_framework.exceptions import ValidationError
from core.utils.response import PrepareResponse
from core.utils.pagination import CustomPagination
from rest_framework.decorators import permission_classes

class ReviewListCreateView(generics.GenericAPIView):
    serializer_class = ReviewSerializer
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        saloon_id = self.kwargs['saloon_id']
        queryset = Review.objects.filter(saloon_id=saloon_id)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = PrepareResponse(
                success=True,
                data=self.get_paginated_response(serializer.data).data,
                message='Reviews fetched successfully'
            )
        else:
            serializer = self.get_serializer(queryset, many=True)
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message='Reviews fetched successfully'
            )
        return response.send(status.HTTP_200_OK)

    @permission_classes([permissions.IsAuthenticated])
    def post(self, request, *args, **kwargs):
        saloon_id = self.kwargs['saloon_id']
        saloon = Saloon.objects.get(id=saloon_id)
        if Review.objects.filter(saloon=saloon, user=self.request.user).exists():
            raise ValidationError("You have already reviewed this saloon.")
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=self.request.user, saloon=saloon)
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message='Review created successfully'
            )
            return response.send(status.HTTP_201_CREATED)
        response = PrepareResponse(
            success=False,
            errors=serializer.errors,
            message='Error creating review'
        )
        return response.send(status.HTTP_400_BAD_REQUEST)

class ReviewDetailView(generics.GenericAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        review_id = self.kwargs['pk']
        review = Review.objects.get(id=review_id, saloon_id=self.kwargs['saloon_id'])
        serializer = self.get_serializer(review)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message='Review fetched successfully'
        )
        return response.send(status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        review_id = self.kwargs['pk']
        review = Review.objects.get(id=review_id, saloon_id=self.kwargs['saloon_id'])
        if review.user != request.user:
            response = PrepareResponse(
                success=False,
                message='You do not have permission to edit this review'
            )
            return response.send(status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message='Review updated successfully'
            )
            return response.send(status.HTTP_200_OK)
        response = PrepareResponse(
            success=False,
            errors=serializer.errors,
            message='Error updating review'
        )
        return response.send(status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        review_id = self.kwargs['pk']
        review = Review.objects.get(id=review_id, saloon_id=self.kwargs['saloon_id'])
        if review.user != request.user:
            response = PrepareResponse(
                success=False,
                message='You do not have permission to delete this review'
            )
            return response.send(status.HTTP_403_FORBIDDEN)
        
        review.delete()
        response = PrepareResponse(
            success=True,
            message='Review deleted successfully'
        )
        return response.send(status.HTTP_204_NO_CONTENT)
