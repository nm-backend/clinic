from django.shortcuts import render, redirect
from .models import Doctor, ServiceDirection, Appointment, OmsDirection, CallbackRequest, Review
from django.contrib import messages
from .forms import OmsApplicationForm
from django.core.paginator import Paginator


def home_view(request):
    doctors = Doctor.objects.all()
    services = ServiceDirection.objects.all()
    return render(request, 'index.html', {
        'doctors': doctors,
        'services': services,
    })


def doctors_page(request):
    doctors = Doctor.objects.all()
    return render(request, 'doctors.html', {'doctors': doctors},)


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
                direction=direction
            )
            messages.success(request, "Вы успешно записались на прием!")
            return redirect('services_list')
    context = {
        'services': services,
    }
    return render(request, 'services.html', context)


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
    return render(
        request,
        "oms.html",
        {
            "form": form,
            "directions": directions,
        },
    )


def dms_page(request):
    return render(request, 'dms.html')


def analysis_page(request):
    return render(request, 'analyses.html')


def promotions_page(request):
    return render(request, 'promotions.html')


def informations_page(request):
    doctors = Doctor.objects.all()
    return render(request, 'legal.html', {'doctors': doctors,})


def about_the_clinic(request):
    return render(request, 'about.html')


def reviews_page(request):
    reviews_list = Review.objects.all().order_by('-id')
    paginator = Paginator(reviews_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'reviews.html', {'page_obj': page_obj})


def contact_page(request):
    doctors = Doctor.objects.all()
    return render(request, 'contacts.html', {'doctors': doctors,})
