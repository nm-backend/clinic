from datetime import date
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from clinics.models import (
    Appointment,
    Clinic,
    ClinicUser,
    Doctor,
    DoctorScheduleSlot,
    Equipment,
    Patient,
    Promotion,
    Review,
    Service,
    ServiceCategory,
)
from api.serializers import (
    AppointmentSerializer,
    ClinicModelSerializer,
    CurrentUserSerializer,
    DoctorModelSerializer,
    EquipmentModelSerializer,
    PromotionModelSerializer,
    RegisterSerializer,
    ReviewModelSerializer,
    ServiceCategoryModelSerializer,
    ServiceModelSerializer,
)


class ClinicListAPIView(APIView):
    def get(self, request):
        clinics = Clinic.objects.filter(is_active=True)
        serializer = ClinicModelSerializer(clinics, many=True)
        return Response(serializer.data)


class DoctorListAPIView(APIView):
    def get(self, request):
        doctors = Doctor.objects.filter(is_active=True, clinic__is_active=True)

        clinic_id = request.query_params.get('clinic_id')
        if clinic_id:
            doctors = doctors.filter(clinic_id=clinic_id)

        specialty = request.query_params.get('specialty')
        if specialty:
            doctors = doctors.filter(specialty__icontains=specialty)

        category_id = request.query_params.get('category_id')
        if category_id:
            doctors = doctors.filter(category_id=category_id)

        serializer = DoctorModelSerializer(doctors, many=True)
        return Response(serializer.data)


class ServiceCategoryListAPIView(APIView):
    def get(self, request):
        categories = ServiceCategory.objects.all()
        serializer = ServiceCategoryModelSerializer(categories, many=True)
        return Response(serializer.data)


class ServiceListAPIView(APIView):
    def get(self, request):
        services = Service.objects.filter(is_active=True)

        clinic_id = request.query_params.get('clinic_id')
        if clinic_id:
            services = services.filter(clinic_id=clinic_id)

        category_id = request.query_params.get('category_id')
        if category_id:
            services = services.filter(category_id=category_id)

        serializer = ServiceModelSerializer(services, many=True)
        return Response(serializer.data)


class AvailableSlotsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        doctor_id = request.query_params.get('doctor_id')
        day_value = request.query_params.get('date')

        if not doctor_id or not day_value:
            raise ValidationError({'doctor_id': 'Обязательный параметр', 'date': 'Обязательный параметр'})

        try:
            day = date.fromisoformat(day_value)
        except ValueError:
            raise ValidationError({'date': 'Неверный формат даты'})

        try:
            doctor = Doctor.objects.get(pk=doctor_id, is_active=True)
        except Doctor.DoesNotExist:
            raise ValidationError({'doctor_id': 'Врач не найден'})

        slots = DoctorScheduleSlot.objects.filter(
            doctor=doctor,
            start_at__date=day,
            is_available=True,
        ).order_by('start_at')

        result = []
        for slot in slots:
            is_busy = Appointment.objects.filter(
                slot=slot,
                status__in=[Appointment.Status.SCHEDULED, Appointment.Status.CONFIRMED],
            ).exists()
            if not is_busy:
                result.append({
                    'id': slot.id,
                    'start': slot.start_at.isoformat(),
                    'end': slot.end_at.isoformat(),
                })

        return Response(result)


class PatientAppointmentsAPIView(APIView):
    def get(self, request):
        patient_id = request.query_params.get('patient_id')
        phone = request.query_params.get('phone')

        appointments = Appointment.objects.all()

        if patient_id:
            appointments = appointments.filter(patient_id=patient_id)
        elif phone:
            appointments = appointments.filter(patient__phone=phone)
        else:
            appointments = appointments.none()

        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)


class PromotionListAPIView(APIView):
    def get(self, request):
        promotions = Promotion.objects.filter(is_active=True)
        serializer = PromotionModelSerializer(promotions, many=True)
        return Response(serializer.data)


class ReviewListAPIView(APIView):
    def get(self, request):
        reviews = Review.objects.filter(is_active=True)
        serializer = ReviewModelSerializer(reviews, many=True)
        return Response(serializer.data)


class EquipmentListAPIView(APIView):
    def get(self, request):
        equipment = Equipment.objects.filter(is_active=True)
        serializer = EquipmentModelSerializer(equipment, many=True)
        return Response(serializer.data)


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        profile = ClinicUser.objects.get(user=user)
        return Response(CurrentUserSerializer(profile).data, status=status.HTTP_201_CREATED)


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        profile = ClinicUser.objects.filter(user=request.user).first()
        if profile is None:
            profile = ClinicUser.objects.create(user=request.user, role=ClinicUser.Role.PATIENT)
        return Response(CurrentUserSerializer(profile).data)