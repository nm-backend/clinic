from django import forms
from .models import OmsApplication, Doctor, ServiceDirection, Review


class OmsApplicationForm(forms.ModelForm):
    class Meta:
        model = OmsApplication
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванова Иван Иванович'
            }),
            'birthdate': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Poshta@gmail.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (___) ___-__-__'
            }),
            'service': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название услуги'
            }),
            'region': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Регион'
            }),
            'doctor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванова Анна +7 (___) ___-__-__'
            }),
            'reason': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Причина обращения'
            }),
            'source': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Источник'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = '__all__'
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванов Иван Иванович'
            }),
            'specialty': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Врач-кардиолог'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'appointment_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/appointment'
            }),
        }


class ServiceDirectionForm(forms.ModelForm):
    class Meta:
        model = ServiceDirection
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Кардиология'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'link_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/service'
            }),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = '__all__'
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванов Иван Иванович'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '30'
            }),
            'doctor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванов Иван Иванович'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Текст отзыва...',
                'rows': 4
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '5',
                'min': 1,
                'max': 5
            }),
        }
