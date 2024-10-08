from rest_framework import generics
from rest_framework.views import APIView
from saloons.models import Saloon,Gallery
from appointments.models import AppointmentSlot,Appointment
from services.models import Service,ServiceVariation, ServiceVariationImage
from openinghours.models import OpeningHour
from staffs.models import Staff,WorkingDay
from moreclub.serializers import (ServiceVariationImageSerializer,
                                   SaloonSerializer,
                                   ServiceSerializer,
                                   StaffSerializer,
                                   OpeningHourSerializer,
                                   WorkingDaySerializer,
                                   ServiceVariationSerializer,
                                   AppointmentSlotByStaffSerializer,
                                   SaloonGallerySerializer,
                                   AppointmentSerializer,
                                   AppointmentDetailsSerializer)
from core.utils.response import PrepareResponse
from rest_framework.permissions import IsAuthenticated
from core.utils.auth import SaloonPermissionMixin
from core.utils.permissions import IsSaloonPermission
from django.shortcuts import get_object_or_404
from django.db import transaction
from datetime import datetime,timedelta
from rest_framework.parsers import MultiPartParser
from django.core.exceptions import PermissionDenied
from core.utils.normalize_text import normalize_amenity




##############Saloon###################################
class SaloonSetupView(SaloonPermissionMixin, generics.ListCreateAPIView):
    serializer_class = SaloonSerializer
    queryset = Saloon.objects.all()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            saloon = serializer.save(user=request.user)
            
            amenities = request.data.getlist('amenities[]')

            normalized_amenities = [normalize_amenity(amenity) for amenity in amenities]


            saloon.amenities = normalized_amenities
            saloon.save()
            saloon_detail = self.get_serializer(saloon).data

           
            return PrepareResponse(
                success=True,
                data=saloon_detail,
                message="Saloon created successfully"
            ).send(201)

        return PrepareResponse(
            success=False,
            data=serializer.errors,
            message="Failed to create saloon"
        ).send(400)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return PrepareResponse(
            success=True,
            data=serializer.data,
            message="List of saloons retrieved successfully"
        ).send(200)

class SaloonDetailUpdateView(SaloonPermissionMixin, generics.RetrieveUpdateAPIView):
    serializer_class = SaloonSerializer

    def get_object(self):
        saloon = get_object_or_404(Saloon, pk=self.kwargs['saloon_id'])
        if saloon.user != self.request.user:
            raise PermissionDenied("You are not authorized to perform this action on this Saloon")
        return saloon

    def get(self, request, *args, **kwargs):
        saloon = self.get_object()
        serializer = self.get_serializer(saloon)
        return PrepareResponse(
            success=True,
            data=serializer.data,
            message='Saloon details fetched successfully'
        ).send(200)

    def patch(self, request, *args, **kwargs):
        saloon = self.get_object()
        serializer = self.get_serializer(saloon, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return PrepareResponse(
                success=True,
                data=serializer.data,
                message='Saloon updated successfully'
            ).send(200)
        return PrepareResponse(
            success=False,
            errors=serializer.errors,
            message='Error updating saloon'
        ).send(400)
    def delete(self,request,*args,**kwargs):
        saloon = self.get_object()
        saloon.delete()
        return PrepareResponse(
            success=True,
            message="Saloon deleted successfully"
        ).send(200)

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
    
################################################ServiceVariations###########################################################

class ServiceVariationListCreateView(generics.GenericAPIView):
    serializer_class = ServiceVariationSerializer
    permission_classes = [IsAuthenticated, IsSaloonPermission]

    def get_queryset(self):
        saloon_id = self.kwargs.get('saloon_id')
        service_id = self.kwargs.get('service_id')
        
        # Use the related service to filter by saloon
        return ServiceVariation.objects.filter(
            service__saloon_id=saloon_id,
            service__saloon__user=self.request.user,
            service_id=service_id
        )

    def get(self, request, *args, **kwargs):
        service_variations = self.get_queryset()
        page = self.paginate_queryset(service_variations)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(service_variations, many=True)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Service variations retrieved successfully"
        )
        return response.send(200)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        saloon_id = self.kwargs.get('saloon_id')
        service_id = self.kwargs.get('service_id')

        try:
            service = Service.objects.get(id=service_id, saloon__user=request.user)
        except Service.DoesNotExist:
            response = PrepareResponse(
                success=False,
                data={},
                message="Service not found or you do not have permission to add variations to this service"
            )
            return response.send(403)

        if serializer.is_valid():
            service_var = serializer.save(service=service)

            images = request.FILES.getlist('images[]')
            if not images:
                response = PrepareResponse(
                    success=False,
                    data=serializer.data,
                    errors={'non_field_errors': ['Please upload at least one image']},
                )
                return response.send(400)

            serializer_data = []
            if not images:
                response = PrepareResponse(
                    success=False,
                    data={},
                    errors={'non_field_errors': ['Please upload at least one image']},
                )
                return response.send(400)
            for image in images:
                serializer_service_var_image = ServiceVariationImageSerializer(data={'variation': service_var.id, 'image': image})
                if serializer_service_var_image.is_valid():
                    serializer_service_var_image.save(variation_id=service_var.id)
                    serializer_data.append(serializer_service_var_image.data)
                else:
                    response = PrepareResponse(
                        success=False,
                        data=serializer_data,
                        errors=serializer_service_var_image.errors
                    )
                    return response.send(400)
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Service variation created successfully"
            )
            return response.send(201)
        else:
            response = PrepareResponse(
                success=False,
                data=serializer.errors,
                message="Failed to create service variation"
            )
            return response.send(400)
        
class ServiceVariationDetailUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = ServiceVariationSerializer
    permission_classes = [IsAuthenticated, IsSaloonPermission]

    def get_object(self):
        service_variation = get_object_or_404(ServiceVariation, pk=self.kwargs['service_variation_id'])
        if service_variation.service.saloon.user != self.request.user:
            response = PrepareResponse(
                success=False,
                message='You are not authorized to perform this action on this service variation'
            )
            return response.send(403)
        return service_variation
    def get(self, request, *args, **kwargs):
        service_variation = self.get_object()
        if isinstance(service_variation, PrepareResponse):
            return service_variation
        serializer = self.get_serializer(service_variation)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message='Service variation fetched successfully'
        )
        return response.send(200)

    def patch(self, request, *args, **kwargs):
        service_variation = self.get_object()
        if isinstance(service_variation, PrepareResponse):
            return service_variation
        serializer = self.get_serializer(service_variation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            images = request.FILES.getlist('images[]')
            remove_images = request.data.getlist('removed_images[]')

            for image in remove_images:
                try:
                    service_variation_image = ServiceVariationImage.objects.get(id=image)
                    service_variation_image.delete()
                except:
                    pass

            serializer_data = []
            for image in images:
                serializer_service_var_image = ServiceVariationImageSerializer(data={'variation': service_variation.id, 'image': image})
                if serializer_service_var_image.is_valid():
                    serializer_service_var_image.save(variation_id=service_variation.id)
                    serializer_data.append(serializer_service_var_image.data)
                else:
                    response = PrepareResponse(
                        success=False,
                        data=serializer_data,
                        errors=serializer_service_var_image.errors
                    )
                    return response.send(400)
            
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message='Service variation updated successfully'
            )
            return response.send(200)

        response = PrepareResponse(
            success=False,
            errors=serializer.errors,
            message='Error updating service variation'
        )
        return response.send(400)
    def delete(self, request, *args, **kwargs):
        service_variation = self.get_object()
        if isinstance(service_variation, PrepareResponse):
            return service_variation
        service_variation.delete()
        response = PrepareResponse(
            success=True,
            data={},
            message='Service variation deleted successfully'
        )
        return response.send(200)
#########################################################Service####################################################################        
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
        return Staff.objects.filter(saloon_id=saloon_id)

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
        saloon_id = self.kwargs.get('saloon_id')
        saloon = get_object_or_404(Saloon, id=saloon_id) 

        staff_serializer = self.get_serializer(data=request.data)
        if staff_serializer.is_valid():
            staff = staff_serializer.save(saloon=saloon)
            services = request.data.getlist('services[]')

            staff_detail = Staff.objects.get(id=staff.id)


            staff_detail.services.set(services)

            response = PrepareResponse(
                success=True,
                data=staff_serializer.data,
                message="Staff created successfully"
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
        staff_id = self.kwargs['staff_id'] 
        staff = get_object_or_404(Staff, pk=staff_id)
        return staff

    def get(self, request, *args, **kwargs):
        saloon_id = self.kwargs.get('saloon_id')
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
            services=request.data.getlist('services[]')
            staff.services.set(services)
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
    

###########################################################staffAvailability########################################
class AppointmentSlotListCreateView(SaloonPermissionMixin, generics.ListCreateAPIView):
    serializer_class = AppointmentSlotByStaffSerializer
    permission_classes = [IsAuthenticated, IsSaloonPermission]

    def get_queryset(self):
        saloon_id = self.kwargs.get('saloon_id')
        staff_id = self.kwargs.get('staff_id')
        staff = get_object_or_404(Staff, id=staff_id, saloon_id=saloon_id)
        working_days = staff.working_days.all()

        available_slots = []
        buffer_time = staff.buffer_time or timedelta(minutes=10)

        for working_day in working_days:
            current_time = working_day.start_time
            end_time = working_day.end_time
            if not current_time or not end_time:
                continue 
            while current_time < end_time:
                for service in staff.services.all():
                    for service_variation in service.variations.all():
                        duration = service_variation.duration
                        slot_end_time = (datetime.combine(datetime.today(), current_time) + duration ).time()
                        print(buffer_time)

                        if slot_end_time <= end_time:
                            # Check if the slot is already booked
                            overlapping_slots = AppointmentSlot.objects.filter(
                                staff=staff,
                                working_day=working_day,
                                start_time__lt=slot_end_time,
                                end_time__gt=current_time
                            )
                            if not overlapping_slots.exists():
                                available_slots.append({
                                    'working_day': working_day,
                                    'staff': staff,
                                    'start_time': current_time,
                                    'end_time': slot_end_time,
                                    'service_variation': service_variation,
                                    'buffer_time': staff.buffer_time
                                })
                        current_time = (datetime.combine(datetime.today(), current_time) + duration + staff.buffer_time).time()

        return available_slots
    
    def get(self, request, *args, **kwargs):
        available_slots = self.get_queryset()
        serializer = self.get_serializer(available_slots, many=True)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Available slots fetched successfully."
        )
        return response.send(200)
class AppointmentSlotDetailUpdateDeleteView(SaloonPermissionMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AppointmentSlotByStaffSerializer
    permission_classes = [IsAuthenticated, IsSaloonPermission]

    def get_object(self):
        saloon_id = self.kwargs['saloon_id']
        slot_id = self.kwargs['slot_id']
        return get_object_or_404(AppointmentSlot, id=slot_id, saloon__id=saloon_id)

    def update(self, request, *args, **kwargs):
        appointment_slot = self.get_object()

        # Ensure that the user updating the slot is the saloon owner
        if appointment_slot.saloon.user != request.user:
            return PrepareResponse(
                success=False,
                message="You are not authorized to update this slot."
            ).send(403)

        serializer = self.get_serializer(appointment_slot, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return PrepareResponse(
                success=True,
                data=serializer.data,
                message="Appointment slot updated successfully."
            ).send(200)
        else:
            return PrepareResponse(
                success=False,
                errors=serializer.errors,
                message="Failed to update appointment slot."
            ).send(400)

    def delete(self, request, *args, **kwargs):
        appointment_slot = self.get_object()
        if appointment_slot.saloon.user != request.user:
            return PrepareResponse(
                success=False,
                message="You are not authorized to delete this slot."
            ).send(403)

        appointment_slot.delete()
        return PrepareResponse(
            success=True,
            message="Appointment slot deleted successfully."
        ).send(200)
    

####################################working days###############################################################
class WorkingDayListCreateView(generics.ListCreateAPIView):
    serializer_class = WorkingDaySerializer
    permission_classes = [IsAuthenticated, IsSaloonPermission]

    def get_queryset(self):
        saloon_id = self.kwargs.get('saloon_id')
        staff_id = self.kwargs.get('staff_id')
        return WorkingDay.objects.filter(staff_id=staff_id, staff__saloon__id=saloon_id)

    def get(self, request, *args, **kwargs):
        working_day = self.get_queryset()
        serializer = self.get_serializer(working_day, many=True)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Working day details retrieved successfully"
        )
        return response.send(200)

    def post(self, request, *args, **kwargs):
        saloon_id = self.kwargs.get('saloon_id')
        staff_id = self.kwargs.get('staff_id')
        saloon = get_object_or_404(Saloon, id=saloon_id)
        staff = get_object_or_404(Staff, id=staff_id, saloon=saloon)

        with transaction.atomic():
            for day_name, hours in request.data.items():
                
                hours = request.data.get(day_name, None)

                if not hours:
                    hours = {
                        'start_time': None,
                        'end_time': None,
                        'is_open': False
                    }
                else:
                    if hours.get('start_time') == "":
                        hours['start_time'] = None
                    if hours.get('end_time') == "":
                        hours['end_time'] = None
                
                day = day_name
                hours['day_of_week'] = day

                serializer = self.get_serializer(data=hours)
                
                if serializer.is_valid():
                    serializer.save(staff=staff)
                else:
                    response = PrepareResponse(
                        success=False,
                        errors=serializer.errors,
                        message=f'Error creating working hours for {day_name}'
                    )
                    return response.send(400)

        response = PrepareResponse(
            success=True,
            message='Working Hours created successfully'
        )
        return response.send(201)
               

class WorkingDayDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkingDaySerializer
    permission_classes = [IsAuthenticated, IsSaloonPermission]

    def get_object(self):
        return get_object_or_404(WorkingDay, pk=self.kwargs['working_day_id'])

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
        saloon_id = self.kwargs.get('saloon_id')
        staff_id = self.kwargs.get('staff_id')
        try:
            saloon = Saloon.objects.get(id=saloon_id)
        except Saloon.DoesNotExist:
            response = PrepareResponse(
                success=False,
                message='Saloon not found',
                errors={'non_field_errors': ['Saloon not found']}
            )
            return response.send(400)
        
        staff = get_object_or_404(Staff, id=staff_id, saloon=saloon)

        if saloon.user != request.user:
            response = PrepareResponse(
                success=False,
                message='You are not authorized to update this saloon',
                errors={'non_field_errors': ['Unauthorized User login']}
            )
            return response.send(403)

        updated_hours = []  

        with transaction.atomic():
            for day_name, partial_data in request.data.items():
                print(f"Received day_name: {day_name} with data: {partial_data}")
                try:
                    working_day = WorkingDay.objects.get(staff=staff, day_of_week=day_name)
                except WorkingDay.DoesNotExist:
                    response = PrepareResponse(
                        success=False,
                        message=f'Working Days not found for {day_name}',
                        errors={'non_field_errors': [f'Working hour not found for {day_name}']}
                    )
                    return response.send(400)
                
                if partial_data.get('is_working') is False:
                    partial_data['start_time'] = '00:00:00'
                    partial_data['end_time'] = '00:00:00'
                else:
                    working_day_start_time_str = partial_data.get('start_time')
                    working_day_end_time_str = partial_data.get('end_time')

                    if working_day_start_time_str and working_day_end_time_str:
                        try:
                            if len(working_day_start_time_str) == 5: 
                                working_day_start_time_str += ':00'
                            if len(working_day_end_time_str) == 5:
                                working_day_end_time_str += ':00'

                            working_day_start_time = datetime.strptime(working_day_start_time_str, '%H:%M:%S').time()
                            working_day_end_time = datetime.strptime(working_day_end_time_str, '%H:%M:%S').time()
                        except ValueError:
                            response = PrepareResponse(
                                success=False,
                                message="Invalid time format. Please use HH:MM or HH:MM:SS format.",
                                errors={'non_field_errors': [f'Invalid time format for {day_name}']}
                            )
                            return response.send(400)
                        opening_hour = OpeningHour.objects.get(saloon=saloon, day_of_week=day_name)
                        if working_day_start_time < opening_hour.start_time or working_day_end_time > opening_hour.end_time:
                            response = PrepareResponse(
                                success=False,
                                message=f"Staff working hours for {day_name} must be within saloon's opening hours ({opening_hour.start_time} - {opening_hour.end_time}).",
                                errors={'non_field_errors': [f"Invalid working hours for {day_name}"]}
                            )
                            return response.send(400)
                serializer = WorkingDaySerializer(working_day, data=partial_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    updated_hours.append(serializer.data)
                else:
                    print(serializer.data)
                    print(serializer.errors)
                    print(day_name)
                    response = PrepareResponse(
                        success=False,
                        errors=serializer.errors,
                        message=f'Error updating working Days for {day_name}'
                    )
                    return response.send(400)
                
        response = PrepareResponse(
            success=True,
            message='Working hours updated successfully',
            data=updated_hours 
        )
        return response.send(200)
    def delete(self, request, *args, **kwargs):
        saloon_id = self.kwargs.get('saloon_id')

        try:
            saloon = Saloon.objects.get(id=saloon_id)
        except Saloon.DoesNotExist:
            response = PrepareResponse(
                success=False,
                message='Saloon not found',
                errors={'non_field_errors': ['Saloon not found']}
            )
            return response.send(400)

        staff = get_object_or_404(Staff, id=self.kwargs.get('staff_id'), saloon=saloon)

        if saloon.user != request.user:
            response = PrepareResponse(
                success=False,
                message='You are not authorized to delete this saloon\'s working hours',
                errors={'non_field_errors': ['Unauthorized User login']}
            )
            return response.send(403)

        with transaction.atomic():
            for day_name in request.data.get('days', []):
                try:
                    opening_hour = OpeningHour.objects.get(staff=staff, day_of_week=day_name)
                    opening_hour.delete()
                except OpeningHour.DoesNotExist:
                    response = PrepareResponse(
                        success=False,
                        message=f"Working Days for {day_name} does not exist."
                    )
                    return response.send(400)

        response = PrepareResponse(
            success=True,
            message="Working hours deleted successfully"
        )
        return response.send(200)

################################################Opening Hours############################################################

class OpeningHourListCreateView(SaloonPermissionMixin, generics.GenericAPIView):
    serializer_class = OpeningHourSerializer

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
        saloon_id = self.kwargs['saloon_id']
        try:
            saloon = Saloon.objects.get(id=saloon_id)
        except Saloon.DoesNotExist:
            response = PrepareResponse(
                success=False,
                message='Saloon not found',
                errors={'non_field_errors': ['Saloon not found']}
            )
            return response.send(400)

        if saloon.user != request.user:
            response = PrepareResponse(
                success=False,
                message='You are not authorized to update this saloon',
                errors={'non_field_errors': ['Unauthorized User login']}
            )
            return response.send(403)

        with transaction.atomic():
            for day_name, hours in request.data.items():
                
                hours = request.data.get(day_name, None)

                if not hours:
                    hours = {
                        'start_time': None,
                        'end_time': None,
                        'is_open': False
                    }
                else:
                    if hours.get('start_time') == "":
                        hours['start_time'] = None
                    if hours.get('end_time') == "":
                        hours['end_time'] = None
                
                day = day_name
                hours['day_of_week'] = day

                serializer = OpeningHourSerializer(data=hours)
                
                if serializer.is_valid():
                    serializer.save(saloon=saloon)
                else:
                    response = PrepareResponse(
                        success=False,
                        errors=serializer.errors,
                        message=f'Error creating working hours for {day_name}'
                    )
                    return response.send(400)

        response = PrepareResponse(
            success=True,
            message='Working Hours created successfully'
        )
        return response.send(201)
    
    def patch(self, request, *args, **kwargs):
        saloon_id = self.kwargs.get('saloon_id')
        try:
            saloon = Saloon.objects.get(id=saloon_id)
        except Saloon.DoesNotExist:
            response = PrepareResponse(
                success=False,
                message='Saloon not found',
                errors={'non_field_errors': ['Saloon not found']}
            )
            return response.send(400)

        if saloon.user != request.user:
            response = PrepareResponse(
                success=False,
                message='You are not authorized to update this saloon',
                errors={'non_field_errors': ['Unauthorized User login']}
            )
            return response.send(403)

        updated_hours = []  

        with transaction.atomic():
            for day_name, partial_data in request.data.items():
                try:
                    opening_hour = OpeningHour.objects.get(saloon=saloon, day_of_week=day_name)
                except OpeningHour.DoesNotExist:
                    response = PrepareResponse(
                        success=False,
                        message=f'Opening hour not found for {day_name}',
                        errors={'non_field_errors': [f'Opening hour not found for {day_name}']}
                    )
                    return response.send(400)
                if partial_data.get('is_open') is False:
                    partial_data['start_time'] = '00:00:00'
                    partial_data['end_time'] = '00:00:00'
                serializer = OpeningHourSerializer(opening_hour, data=partial_data, partial=True)

                if serializer.is_valid():
                    serializer.save()
                    updated_hours.append(serializer.data)
                else:
                    response = PrepareResponse(
                        success=False,
                        errors=serializer.errors,
                        message=f'Error updating working hours for {day_name}'
                    )
                    return response.send(400)
        response = PrepareResponse(
            success=True,
            message='Opening hours updated successfully',
            data=updated_hours 
        )
        return response.send(200)
    def delete(self, request, *args, **kwargs):
        saloon_id = self.kwargs.get('saloon_id')

        try:
            saloon = Saloon.objects.get(id=saloon_id)
        except Saloon.DoesNotExist:
            response = PrepareResponse(
                success=False,
                message='Saloon not found',
                errors={'non_field_errors': ['Saloon not found']}
            )
            return response.send(400)

        if saloon.user != request.user:
            response = PrepareResponse(
                success=False,
                message='You are not authorized to delete this saloon\'s opening hours',
                errors={'non_field_errors': ['Unauthorized User login']}
            )
            return response.send(403)

        with transaction.atomic():
            for day_name in request.data.get('days', []):
                try:
                    opening_hour = OpeningHour.objects.get(saloon=saloon, day_of_week=day_name)
                    opening_hour.delete()
                except OpeningHour.DoesNotExist:
                    response = PrepareResponse(
                        success=False,
                        message=f"Opening hour for {day_name} does not exist."
                    )
                    return response.send(400)

        response = PrepareResponse(
            success=True,
            message="Opening hours deleted successfully"
        )
        return response.send(200)
######################################################Gallery###############################################
class SaloonGalleryListCreateView(SaloonPermissionMixin, generics.GenericAPIView):
    serializer_class = SaloonGallerySerializer
    parser_classes = (MultiPartParser,)

    def get_object(self):
        saloon_id = self.kwargs['saloon_id']
        gallery_id = self.kwargs['gallery_id']
        return get_object_or_404(Gallery, saloon_id=saloon_id, id=gallery_id)

    def get(self, request, *args, **kwargs):
        saloon_id = self.kwargs['saloon_id']
        saloon = Saloon.objects.get(id=saloon_id)

        if saloon.user != request.user:
            return PrepareResponse(
                success=False,
                message='You are not authorized to update this saloon'
            ).send(403)

        images = Gallery.objects.filter(saloon=saloon)
        serializer = SaloonGallerySerializer(images, many=True, context={'request': request})  # Pass request context
        return PrepareResponse(
            success=True,
            data=serializer.data,
            message='Gallery images fetched successfully'
        ).send(200)

    def post(self, request, *args, **kwargs):
        saloon_id = self.kwargs['saloon_id']
        saloon = Saloon.objects.get(id=saloon_id)

        if saloon.user != request.user:
            return PrepareResponse(
                success=False,
                message='You are not authorized to update this saloon'
            ).send(403)

        # Use 'images' instead of 'images[]'
        images = request.FILES.getlist('images[]')
        print(f"Images: {images}")  # Debugging line to check if images are coming through

        if not images:
            return PrepareResponse(
                success=False,
                message='No images provided',
            ).send(400)

        serializer_data = []
        for image in images:
            serializer = SaloonGallerySerializer(data={'images': image}, context={'request': request})
            if serializer.is_valid():
                serializer.save(saloon=saloon)
                serializer_data.append(serializer.data)
            else:
                return PrepareResponse(
                    success=False,
                    errors=serializer.errors,
                    message=f'Error uploading image {image.name}'
                ).send(400)

        return PrepareResponse(
            success=True,
            data=serializer_data,
            message=f'{len(images)} images uploaded successfully'
        ).send(201)
class SaloonGalleryDetailUpdateView(SaloonPermissionMixin, generics.GenericAPIView):
        serializer_class = SaloonGallerySerializer
        parser_classes = (MultiPartParser,)

        def patch(self, request, *args, **kwargs):
            saloon_id = self.kwargs['saloon_id']
            gallery_id = self.kwargs['gallery_id']
            saloon = Saloon.objects.get(id=saloon_id)

            if saloon.user != request.user:
                return PrepareResponse(
                    success=False,
                    message='You are not authorized to update this saloon'
                ).send(403)

            gallery = Gallery.objects.get(id=gallery_id, saloon=saloon)
            serializer = self.get_serializer(gallery, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save() 
                return PrepareResponse(
                    success=True,
                    data=serializer.data,
                    message='Gallery image updated successfully'
                ).send(200)
            else:
                return PrepareResponse(
                    success=False,
                    errors=serializer.errors,
                    message='Failed to update gallery image'
                ).send(400)
        
        def delete(self, request, *args, **kwargs):
            saloon_id = self.kwargs['saloon_id']
            gallery_id = self.kwargs['gallery_id']
            saloon = Saloon.objects.get(id=saloon_id)

            if saloon.user != request.user:
                return PrepareResponse(
                    success=False,
                    message='You are not authorized to delete this image'
                ).send(403)
            gallery = Gallery.objects.get(id=gallery_id, saloon=saloon)
            gallery.delete() 

            return PrepareResponse(
                success=True,
                message='Gallery image deleted successfully'
            ).send(200)
        
class SaloonAppointmentListView(SaloonPermissionMixin,generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated,IsSaloonPermission]

    def get_queryset(self):
        saloon_id = self.kwargs['saloon_id']
        return Appointment.objects.filter(saloon_id=saloon_id)

    def get(self, request, *args, **kwargs):
        saloon_id = self.kwargs['saloon_id']
        saloon = Saloon.objects.get(id=saloon_id)

        if saloon.user != request.user:
            return PrepareResponse(
                success=False,
                message='You are not authorized to view this saloon'
            ).send(403)
        appointments = Appointment.objects.filter(saloon_id=saloon_id)
        serializer = AppointmentSerializer(appointments, many=True)
        return PrepareResponse(
            success=True,
            data=serializer.data,
            message='Appointments fetched successfully'
        ).send(200)
    
class StaffAppointmentListView(SaloonPermissionMixin,generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated,IsSaloonPermission]

    def get_queryset(self):
        saloon_id = self.kwargs['saloon_id']
        staff_id = self.kwargs['staff_id']
        return Staff.objects.filter(saloon_id=saloon_id, id=staff_id)

    def get(self, request, *args, **kwargs):
        saloon_id = self.kwargs['saloon_id']
        staff_id = self.kwargs['staff_id']
        saloon = Saloon.objects.get(id=saloon_id)

        if saloon.user != request.user:
            return PrepareResponse(
                success=False,
                message='You are not authorized to view this saloon'
            ).send(403)
        appointments = Appointment.objects.filter(saloon_id=saloon_id, staff_id=staff_id)
        serializer = AppointmentSerializer(appointments, many=True)
        return PrepareResponse(
            success=True,
            data=serializer.data,
            message='Appointments fetched successfully'
        ).send(200)
    
class AppointmentDetailListView(SaloonPermissionMixin,generics.ListCreateAPIView):
    serializer_class = AppointmentDetailsSerializer
    permission_classes = [IsAuthenticated,IsSaloonPermission]

    def get_queryset(self):
        saloon_id = self.kwargs['saloon_id']
        appointment_id = self.kwargs['appointment_id']
        return Appointment.objects.filter(saloon_id=saloon_id, id=appointment_id)

    def get(self, request, *args, **kwargs):
        saloon_id = self.kwargs['saloon_id']
        appointment_id = self.kwargs['appointment_id']
        saloon = Saloon.objects.get(id=saloon_id)

        if saloon.user != request.user:
            return PrepareResponse(
                success=False,
                message='You are not authorized to view this saloon'
            ).send(403)
        appointments = Appointment.objects.get(saloon_id=saloon_id, id=appointment_id)
        serializer = AppointmentDetailsSerializer(appointments)
        return PrepareResponse(
            success=True,
            data=serializer.data,
            message='Appointments fetched successfully'
        ).send(200)
    
    
        
    





    

