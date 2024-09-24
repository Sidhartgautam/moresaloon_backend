from rest_framework import generics
from rest_framework.views import APIView
from saloons.models import Saloon
from services.models import Service
from staffs.models import Staff,WorkingDay
from moreclub.serializers import SaloonSerializer,ServiceSerializer
from core.utils.response import PrepareResponse
from rest_framework.permissions import IsAuthenticated
from core.utils.pagination import CustomPageNumberPagination
from core.utils.auth import SaloonPermissionMixin
from core.utils.permissions import IsSaloonPermission
from django.shortcuts import get_object_or_404
from staffs.serializers import StaffSerializer,WorkingDaySerializer



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

class UserSaloonListView(generics.GenericAPIView):
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
class ServiceListCreateView(generics.ListCreateAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated, IsSaloonPermission]

    def get_queryset(self):
        return Service.objects.filter(saloon__user=self.request.user)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Get the salon related to the current user
            saloon = request.user.saloons.first()  # Modify as per your relationship

            # Create the service
            serializer.save(saloon=saloon)

            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Service created successfully with variations"
            )
            return response.send(201)

        response = PrepareResponse(
            success=False,
            data=serializer.errors,
            message="Failed to create service"
        )
        return response.send(400)

class ServiceDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated, IsSaloonPermission]

    def get_queryset(self):
        return Service.objects.filter(saloon__user=self.request.user)

    def patch(self, request, *args, **kwargs):
        service = self.get_object()
        serializer = self.get_serializer(service, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Service updated successfully"
            )
            return response.send(200)

        response = PrepareResponse(
            success=False,
            data=serializer.errors,
            message="Failed to update service"
        )
        return response.send(400)

    def delete(self, request, *args, **kwargs):
        service = self.get_object()
        service.delete()

        response = PrepareResponse(
            success=True,
            message="Service deleted successfully"
        )
        return response.send(200)
    
    ####################################staffs###############################################################

    class StaffDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
        serializer_class = StaffSerializer
        permission_classes = [IsAuthenticated, IsSaloonPermission]

        def get_object(self):
            # Fetch staff member only if they belong to the current user's salon
            staff = get_object_or_404(Staff, pk=self.kwargs['staff_id'], saloon__user=self.request.user)
            return staff

        def get(self, request, *args, **kwargs):
            staff = self.get_object()
            serializer = self.get_serializer(staff)
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Staff details fetched successfully"
            )
            return response.send(200)

        def patch(self, request, *args, **kwargs):
            staff = self.get_object()
            serializer = self.get_serializer(staff, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                response = PrepareResponse(
                    success=True,
                    data=serializer.data,
                    message="Staff updated successfully"
                )
                return response.send(200)

            response = PrepareResponse(
                success=False,
                data=serializer.errors,
                message="Failed to update staff"
            )
            return response.send(400)

        def delete(self, request, *args, **kwargs):
            staff = self.get_object()
            staff.delete()
            response = PrepareResponse(
                success=True,
                message="Staff deleted successfully"
            )
            return response.send(200)
        

class WorkingDayDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkingDaySerializer
    permission_classes = [IsAuthenticated, IsSaloonPermission]

    def get_object(self):
        return get_object_or_404(WorkingDay, pk=self.kwargs['working_day_id'], staff__saloon__user=self.request.user)

    def get(self, request, *args, **kwargs):
        working_day = self.get_object()
        serializer = self.get_serializer(working_day)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Working day details fetched successfully"
        )
        return response.send(200)

    def patch(self, request, *args, **kwargs):
        working_day = self.get_object()
        serializer = self.get_serializer(working_day, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Working day updated successfully"
            )
            return response.send(200)
        response = PrepareResponse(
            success=False,
            data=serializer.errors,
            message="Failed to update working day"
        )
        return response.send(400)

    def delete(self, request, *args, **kwargs):
        working_day = self.get_object()
        working_day.delete()
        response = PrepareResponse(
            success=True,
            message="Working day deleted successfully"
        )
        return response.send(200)

