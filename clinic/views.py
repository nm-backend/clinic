from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Doctor, ServiceDirection, Appointment, OmsDirection, CallbackRequest, Review
from .forms import OmsApplicationForm, DoctorForm, ServiceDirectionForm, ReviewForm


def home_view(request):
    doctors = Doctor.objects.all()
    services = ServiceDirection.objects.all()
    return render(request, 'index.html', {
        'doctors': doctors,
        'services': services,
    })


def save_callback(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        if name and phone:
            CallbackRequest.objects.create(name=name, phone=phone)
            referer = request.META.get('HTTP_REFERER', '/')
            if '?' in referer:
                redirect_url = f"{referer}&success=1"
            else:
                redirect_url = f"{referer}?success=1"
            return redirect(redirect_url)
    return redirect(request.META.get('HTTP_REFERER', '/'))


def save_appointment(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        direction = request.POST.get('direction')
        if full_name and phone and direction:
            Appointment.objects.create(
                full_name=full_name,
                phone=phone,
                direction=direction,
            )
            referer = request.META.get('HTTP_REFERER', '/')
            if '?' in referer:
                redirect_url = f"{referer}&success=1"
            else:
                redirect_url = f"{referer}?success=1"
            return redirect(redirect_url)
    return redirect(request.META.get('HTTP_REFERER', '/'))


def direction_page(request):
    return render(request, 'direction_detail.html')


def oms_page(request):
    if request.method == "POST":
        form = OmsApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Ваша заявка успешно отправлена!")
            return redirect("oms_page")
    else:
        form = OmsApplicationForm()
    directions = OmsDirection.objects.all()
    return render(request, "oms.html", {
        "form": form,
        "directions": directions,
    })


def dms_page(request):
    return render(request, 'dms.html')


def analysis_page(request):
    return render(request, 'analyses.html')


def promotions_page(request):
    return render(request, 'promotions.html')


def informations_page(request):
    doctors = Doctor.objects.all()
    return render(request, 'legal.html', {'doctors': doctors})


def about_the_clinic(request):
    return render(request, 'about.html')


def contact_page(request):
    doctors = Doctor.objects.all()
    return render(request, 'contacts.html', {'doctors': doctors})


def services_list(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        direction = request.POST.get('direction')
        if full_name and phone and direction:
            Appointment.objects.create(
                full_name=full_name,
                phone=phone,
                direction=direction,
            )
            messages.success(request, "Вы успешно записались на прием!")
        else:
            messages.error(request, "Заполните все поля.")
        return redirect('services_list')
    services = ServiceDirection.objects.all()
    return render(request, 'services.html', {'services': services})


def reviews_page(request):
    paginator = Paginator(Review.objects.all(), 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'reviews.html', {'page_obj': page_obj})


def delete_doctor(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        doctor.delete()
        return redirect('doctors_list')
    return render(request, 'doctor_confirm_delete.html', {'object': doctor})


def delete_service(request, pk):
    service = get_object_or_404(ServiceDirection, pk=pk)
    if request.method == 'POST':
        service.delete()
        return redirect('services_list')
    return render(request, 'service_confirm_delete.html', {'object': service})


def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        review.delete()
        return redirect('reviews')
    return render(request, 'review_confirm_delete.html', {'object': review})


class DoctorListView(ListView):
    model = Doctor
    template_name = 'doctors.html'
    context_object_name = 'doctors'
    paginate_by = 10
    ordering = ['full_name']


class DoctorDetailView(DetailView):
    model = Doctor
    template_name = 'doctor_detail.html'
    context_object_name = 'doctor'


class DoctorCreateView(CreateView):
    model = Doctor
    form_class = DoctorForm
    template_name = 'doctor_form.html'
    success_url = reverse_lazy('doctors_list')


class DoctorUpdateView(UpdateView):
    model = Doctor
    form_class = DoctorForm
    template_name = 'doctor_form.html'
    success_url = reverse_lazy('doctors_list')


class ServiceDirectionDetailView(DetailView):
    model = ServiceDirection
    template_name = 'direction_detail.html'
    context_object_name = 'service'


class ServiceDirectionCreateView(CreateView):
    model = ServiceDirection
    form_class = ServiceDirectionForm
    template_name = 'service_form.html'
    success_url = reverse_lazy('services_list')


class ServiceDirectionUpdateView(UpdateView):
    model = ServiceDirection
    form_class = ServiceDirectionForm
    template_name = 'service_form.html'
    success_url = reverse_lazy('services_list')


class ReviewDetailView(DetailView):
    model = Review
    template_name = 'review_detail.html'
    context_object_name = 'review'


class ReviewCreateView(CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'review_form.html'
    success_url = reverse_lazy('reviews')


class ReviewUpdateView(UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'review_form.html'
    success_url = reverse_lazy('reviews')
