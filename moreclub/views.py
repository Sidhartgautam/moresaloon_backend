from rest_framework import generics
from saloons.models import Saloon
from moreclub.serializers import SaloonSerializer
from core.utils.response import PrepareResponse
from core.utils.pagination import CustomPageNumberPagination
from core.utils.auth import SaloonPermissionMixin
from core.utils.permissions import IsSaloonPermission
from django.shortcuts import get_object_or_404


##############Saloon###################################
class SaloonSetupView(SaloonPermissionMixin, generics.CreateAPIView):
    serailizer_class =SaloonSerializer

    def post(self,request,*args,**kwargs):
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response=PrepareResponse(
                success=True,
                data=serializer.data,
                message="Saloon created successfully"
            )
            return response.send(201)
        response = PrepareResponse(
            success=False,
            data=serializer.errors,
            message="Failed to create saloon"
        )
        return response.send(400)

class SaloonDetailUpdateView(SaloonPermissionMixin,generics.RetrieveUpdateAPIView):
    serializer_class=SaloonSerializer

    def get_object(self):
        saloon = get_object_or_404(Saloon, pk=self.kwargs['saloon_id'])
        if saloon.user != self.request.user:
            response = PrepareResponse(
                success=False,
                message='You are not authorized to perform this action on this Saloon'
            )
            return response.send(403)
        return Saloon
    
    def get(self,request,*args,**kwargs):
        saloon=self.get_object()
        if isinstance(saloon,PrepareResponse):
            return saloon
        serializer=self.get_serializer(saloon)
        response=PrepareResponse(
            success=True,
            data=serializer.data,
            message='Salooon details fetched Sucessfully'
        )
        return response.send(200)
    def patch(self,request,*args,**kwargs):
        saloon=self.get_object()
        if isinstance(saloon,PrepareResponse):
            return saloon
        serializer=self.get_serializer(saloon,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            response=PrepareResponse(
                success=True,
                data=serializer.data,
                message='Saloon updated sucessfully'
            )
            return response.send(200)
        
        response=PrepareResponse(
            success=False,
            errors=serializer.errors,
            message='Error updating restaurant'
        )
        return response.send(400)

class UserSaloonListView(generics.GenericsAPIView):
    serializer_class = SaloonSerializer
    def get(self,request,*args,**kwargs):
        saloon = Saloon.objects.filter(user=request.user)
        serializer=self.get_serialzier(saloon,many=True)
        response=PrepareResponse(
            success=True,
            data=serializer.data,
            message='User Saloons fetched sucessfully'
        )
        return response.send(200)
    
################################################Service###########################################################
# class UserServiceRetriveUpdateDestroyView(SaloonPermissionMixin,generics.RetrieveUpdateAPIView):

    

