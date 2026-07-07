from django.db import models

class Clinic(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=500)
    phone = models.CharField(max_length=30)
    
    def __str__(self):
        return self.name

class Doctor(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=150)
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Service(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.name

class Appointment(models.Model):
    patient_name = models.CharField(max_length=150)
    patient_phone = models.CharField(max_length=30)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    scheduled_at = models.DateTimeField()
    
    def __str__(self):
        return f'{self.patient_name} - {self.doctor.last_name}'
