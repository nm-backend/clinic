from rest_framework import viewsets
from django.shortcuts import render
from .models import Clinic, Doctor, Service, Appointment
from .serializers import ClinicSerializer, DoctorSerializer, ServiceSerializer, AppointmentSerializer

def index(request):
    return render(request, 'index.html')

class ClinicViewSet(viewsets.ModelViewSet):
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
