from rest_framework import generics
from rest_framework.views import APIView
from saloons.models import Saloon
from services.models import Service
from openinghours.models import OpeningHour
from staffs.models import Staff,WorkingDay
from moreclub.serializers import SaloonSerializer,ServiceSerializer,StaffSerializer,OpeningHourSerializer,WorkingDaySerializer
from core.utils.response import PrepareResponse
from rest_framework.permissions import IsAuthenticated
from core.utils.auth import SaloonPermissionMixin
from core.utils.permissions import IsSaloonPermission
from django.shortcuts import get_object_or_404



##############Saloon###################################
class SaloonSetupView(SaloonPermissionMixin, generics.GenericAPIView):
    serializer_class =SaloonSerializer

    def post(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
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

class SaloonDetailUpdateView(SaloonPermissionMixin, generics.RetrieveUpdateAPIView):
    serializer_class = SaloonSerializer

    def get_object(self):
        saloon = get_object_or_404(Saloon, pk=self.kwargs['saloon_id'])
        if saloon.user != self.request.user:
            response = PrepareResponse(
                success=False,
                message='You are not authorized to perform this action on this Saloon'
            )
            return response.send(403)
        return saloon  

    def get(self, request, *args, **kwargs):
        saloon = self.get_object()
        if isinstance(saloon, PrepareResponse):
            return saloon
        serializer = self.get_serializer(saloon)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message='Saloon details fetched successfully'
        )
        return response.send(200)

    def patch(self, request, *args, **kwargs):
        saloon = self.get_object()
        if isinstance(saloon, PrepareResponse):
            return saloon
        serializer = self.get_serializer(saloon, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message='Saloon updated successfully'
            )
            return response.send(200)

        response = PrepareResponse(
            success=False,
            errors=serializer.errors,
            message='Error updating saloon'
        )
        return response.send(400)

class UserSaloonListView(SaloonPermissionMixin, generics.GenericAPIView):
    serializer_class = SaloonSerializer
    def get(self, request, *args, **kwargs):
        saloon = Saloon.objects.filter(user=request.user)
        serializer=self.get_serializer(saloon, many=True)
        response=PrepareResponse(
            success=True,
            data=serializer.data,
            message='User Saloons fetched sucessfully'
        )
        return response.send(200)
    
################################################Service###########################################################
class ServiceListCreateView(generics.GenericAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated, IsSaloonPermission]

    def get_queryset(self):
        saloon_id = self.kwargs.get('saloon_id')
        return Service.objects.filter(saloon__user=self.request.user, saloon_id=saloon_id)

    def get(self, request, *args, **kwargs):
        services = self.get_queryset()
        page = self.paginate_queryset(services)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(services, many=True)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Services retrieved successfully"
        )
        return response.send(200)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        saloon_id = self.kwargs.get('saloon_id')

        try:
            saloon = Saloon.objects.get(id=saloon_id, user=request.user)
        except Saloon.DoesNotExist:
            response = PrepareResponse(
                success=False,
                data={},
                message="Saloon not found or you do not have permission to add services to this saloon"
            )
            return response.send(403)

        if serializer.is_valid():
            # Create the service for the specified saloon
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
        saloon_id = self.kwargs.get('saloon_id')
        return Service.objects.filter(saloon__id=saloon_id, saloon__user=self.request.user)

    def get(self, request, *args, **kwargs):
        service = self.get_object()
        serializer = self.get_serializer(service)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Service details fetched successfully"
        )
        return response.send(200)

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

class StaffCreateView(generics.GenericAPIView):
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated, IsSaloonPermission]

    def get_queryset(self):
        saloon_id = self.kwargs.get('saloon_id')
        return Staff.objects.filter(saloon_id=saloon_id, saloon__user=self.request.user)

    def get(self, request, *args, **kwargs):
        staff = self.get_queryset()
        serializer = self.get_serializer(staff, many=True)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Staff details retrieved successfully"
        )
        return response.send(200)

    def post(self, request, *args, **kwargs):
        staff_serializer = self.get_serializer(data=request.data)   
        if staff_serializer.is_valid():
            staff = staff_serializer.save()
            working_days_data = request.data.get('working_days', [])
            for working_day_data in working_days_data:
                working_day_data['staff'] = staff.id
                working_day_serializer = WorkingDaySerializer(data=working_day_data)
                if working_day_serializer.is_valid():
                    working_day_serializer.save()
                else:
                    response = PrepareResponse(
                        success=False,
                        data=working_day_serializer.errors,
                        message="Failed to create working days"
                    )
                    return response.send(400)

            response = PrepareResponse(
                success=True,
                data=staff_serializer.data,
                message="Staff created successfully with working days"
            )
            return response.send(201)

        response = PrepareResponse(
            success=False,
            data=staff_serializer.errors,
            message="Failed to create staff"
        )
        return response.send(400)
    
class StaffDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated, IsSaloonPermission]

    def get_object(self):
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
        return get_object_or_404(WorkingDay, pk=self.kwargs['working_day_id'], staff_saloon_user=self.request.user)

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
    

#########################################Appointments and Appointments Slots#############################################

# class AppointmenntSlotListCreateView(generics.ListCreateAPIView):
#     serializer_class = AppointmentSlotSerializer
#     permission_classes = [IsAuthenticated, IsSaloonPermission]

#     def get_queryset(self):
#         return AppointmentSlot.objects.filter(staff_saloon_user=self.request.user)

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)

#         if serializer.is_valid():
#             serializer.save()
#             response = PrepareResponse(
#                 success=True,
#                 data=serializer.data,
#                 message="Appointment slot created successfully"
#             )
#             return response.send(201)

#         response = PrepareResponse(
#             success=False,
#             data=serializer.errors,
#             message="Failed to create appointment slot"
#         )

################################################Opening Hours############################################################

class OpeningHourListCreateView(generics.GenericAPIView):
    serializer_class = OpeningHourSerializer
    permission_classes = [IsAuthenticated, IsSaloonPermission]

    def get_queryset(self):
        saloon_id = self.kwargs.get('saloon_id')
        return OpeningHour.objects.filter(saloon__user=self.request.user, saloon_id=saloon_id)

    def get(self, request, *args, **kwargs):
        opening_hours = self.get_queryset()
        page = self.paginate_queryset(opening_hours)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(opening_hours, many=True)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Opening hours retrieved successfully"
        )
        return response.send(200)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        saloon_id = self.kwargs.get('saloon_id')

        try:
            saloon = Saloon.objects.get(id=saloon_id, user=request.user)
        except Saloon.DoesNotExist:
            response = PrepareResponse(
                success=False,
                data={},
                message="Saloon not found or you do not have permission to add opening hours to this saloon"
            )
            return response.send(403)

        if serializer.is_valid():
            # Create the opening hour for the specified saloon
            serializer.save(saloon=saloon)

            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Opening hour created successfully"
            )
            return response.send(201)

        response = PrepareResponse(
            success=False,
            data=serializer.errors,
            message="Failed to create opening hour"
        )
        return response.send(400)
    
class OpeningHourDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OpeningHourSerializer
    permission_classes = [IsAuthenticated, IsSaloonPermission]

    def get_object(self):
        saloon_id = self.kwargs.get('saloon_id')
        opening_hour_id = self.kwargs.get('opening_hour_id')
        return get_object_or_404(OpeningHour, id=opening_hour_id, saloon__user=self.request.user, saloon_id=saloon_id)

    def get(self, request, *args, **kwargs):
        opening_hour = self.get_object()
        serializer = self.get_serializer(opening_hour)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Opening hour details fetched successfully"
        )
        return response.send(200)

    def patch(self, request, *args, **kwargs):
        opening_hour = self.get_object()
        serializer = self.get_serializer(opening_hour, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Opening hour updated successfully"
            )
            return response.send(200)

        response = PrepareResponse(
            success=False,
            data=serializer.errors,
            message="Failed to update opening hour"
        )
        return response.send(400)

    def delete(self, request, *args, **kwargs):
        opening_hour = self.get_object()
        opening_hour.delete()
        response = PrepareResponse(
            success=True,
            message="Opening hour deleted successfully"
        )
        return response.send(200)