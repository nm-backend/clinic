from django.contrib.auth.models import User
from rest_framework import generics, permissions, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from .models import (
    Doctor,
    ServiceDirection,
    Appointment,
    OmsDirection,
    OmsApplication,
    CallbackRequest,
    Review,
)
from .serializers import (
    RegisterSerializer,
    DoctorSerializer,
    ServiceDirectionSerializer,
    AppointmentSerializer,
    OmsDirectionSerializer,
    OmsApplicationSerializer,
    CallbackRequestSerializer,
    ReviewSerializer,
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class DoctorViewSet(generics.CreateAPIView, generics.ListAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['full_name', 'specialty']
    ordering_fields = ['full_name', 'specialty']


class ServiceDirectionViewSet(generics.CreateAPIView, generics.ListAPIView):
    queryset = ServiceDirection.objects.all()
    serializer_class = ServiceDirectionSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['title']


class OmsDirectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OmsDirection.objects.all()
    serializer_class = OmsDirectionSerializer


class ReviewViewSet(generics.CreateAPIView, generics.ListAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Appointment.objects.all()
        return Appointment.objects.filter(patient=self.request.user)


class CallbackCreateView(generics.CreateAPIView):
    queryset = CallbackRequest.objects.all()
    serializer_class = CallbackRequestSerializer
    permission_classes = [permissions.AllowAny]


class OmsApplicationCreateView(generics.CreateAPIView):
    queryset = OmsApplication.objects.all()
    serializer_class = OmsApplicationSerializer
    permission_classes = [permissions.AllowAny]
