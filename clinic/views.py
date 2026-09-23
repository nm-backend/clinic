from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
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


def services_list(request):
    services = ServiceDirection.objects.all()
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        direction = request.POST.get("direction")
        if full_name and phone and direction:
            Appointment.objects.create(
                full_name=full_name,
                phone=phone,
                direction=direction,
            )
            messages.success(request, "Вы успешно записались на прием!")
            return redirect('services_list')
    return render(request, 'services.html', {'services': services})


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


class DoctorDeleteView(DeleteView):
    model = Doctor
    template_name = 'doctor_confirm_delete.html'
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


class ServiceDirectionDeleteView(DeleteView):
    model = ServiceDirection
    template_name = 'service_confirm_delete.html'
    success_url = reverse_lazy('services_list')


class ReviewListView(ListView):
    model = Review
    template_name = 'reviews.html'
    context_object_name = 'page_obj'
    paginate_by = 10
    ordering = ['-created_at']


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


class ReviewDeleteView(DeleteView):
    model = Review
    template_name = 'review_confirm_delete.html'
    success_url = reverse_lazy('reviews')
