from rest_framework.viewsets import ModelViewSet

from clinics.models import Appointment, CallbackRequest
from api.serializers import AppointmentSerializer, CallbackRequestModelSerializer


class AppointmentViewSet(ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        appointments = super().get_queryset()

        patient_phone = self.request.query_params.get('patient_phone')
        if patient_phone:
            appointments = appointments.filter(patient__phone=patient_phone)

        appointment_status = self.request.query_params.get('status')
        if appointment_status:
            appointments = appointments.filter(status=appointment_status)

        return appointments


class CallbackRequestViewSet(ModelViewSet):
    queryset = CallbackRequest.objects.all()
    serializer_class = CallbackRequestModelSerializer

    def get_queryset(self):
        if not self.request.user.is_staff:
            return CallbackRequest.objects.none()
        return CallbackRequest.objects.all()