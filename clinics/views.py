from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from clinics.models import (
    CallbackRequest,
    Doctor,
    Equipment,
    Promotion,
    Review,
    Service,
    ServiceCategory,
)
from api.serializers import CallbackRequestModelSerializer


def index(request):
    categories = ServiceCategory.objects.all()[:8]
    doctors = Doctor.objects.filter(is_active=True, clinic__is_active=True)[:8]
    equipment = Equipment.objects.filter(is_active=True)
    context = {
        'categories': categories,
        'doctors': doctors,
        'equipment': equipment,
        'promotions': Promotion.objects.filter(is_active=True),
    }
    return render(request, 'index.html', context)


def directions(request):
    return redirect('services')


def direction_detail(request, slug):
    category = get_object_or_404(ServiceCategory, slug=slug)
    doctors = Doctor.objects.filter(category=category, is_active=True, clinic__is_active=True)
    services = Service.objects.filter(category=category, is_active=True)
    reviews = Review.objects.filter(doctor__category=category, is_active=True)[:3]
    context = {
        'category': category,
        'doctors': doctors,
        'services': services,
        'reviews': reviews,
    }
    return render(request, 'direction_detail.html', context)


def doctors(request):
    doctors = Doctor.objects.filter(is_active=True, clinic__is_active=True)
    category_slug = request.GET.get('category')
    if category_slug:
        doctors = doctors.filter(category__slug=category_slug)
    search = request.GET.get('q', '').strip()
    if search:
        doctors = doctors.filter(last_name__icontains=search)
    context = {
        'doctors': doctors,
        'categories': ServiceCategory.objects.all(),
        'active_category': category_slug,
        'search': search,
    }
    return render(request, 'doctors.html', context)


def services(request):
    categories = ServiceCategory.objects.all()
    all_services = Service.objects.filter(is_active=True)
    grouped_services = []
    for category in categories:
        services_in_category = all_services.filter(category=category)
        grouped_services.append({'category': category, 'services': services_in_category})
    context = {'grouped_services': grouped_services}
    return render(request, 'services.html', context)


def service_detail(request, pk):
    return redirect('services')


def promotions(request):
    promotions = Promotion.objects.filter(is_active=True)
    return render(request, 'promotions.html', {'promotions': promotions})


def about(request):
    reviews = Review.objects.filter(is_active=True)[:3]
    return render(request, 'about.html', {'reviews': reviews})


def reviews(request):
    reviews = Review.objects.filter(is_active=True)
    return render(request, 'reviews.html', {'reviews': reviews})


def contacts(request):
    doctors = Doctor.objects.filter(is_active=True, clinic__is_active=True)[:8]
    return render(request, 'contacts.html', {'doctors': doctors})


def oms(request):
    return render(request, 'oms.html')


def dms(request):
    return render(request, 'dms.html')


def analyses(request):
    return render(request, 'analyses.html')


def legal(request):
    return render(request, 'legal.html')


def appointment_page(request):
    return redirect('oms')


@require_POST
def appointment_request(request):
    serializer = CallbackRequestModelSerializer(data={
        'request_type': CallbackRequest.Type.APPOINTMENT,
        'full_name': request.POST.get('full_name', '').strip(),
        'phone': request.POST.get('phone', '').strip(),
    })
    if serializer.is_valid():
        serializer.save()
    return redirect(request.POST.get('next', '/'))


@require_POST
def callback_request(request):
    serializer = CallbackRequestModelSerializer(data={
        'request_type': CallbackRequest.Type.CALLBACK,
        'full_name': request.POST.get('full_name', '').strip(),
        'phone': request.POST.get('phone', '').strip(),
        'comment': request.POST.get('comment', '').strip(),
    })
    if serializer.is_valid():
        serializer.save()
    return redirect(request.POST.get('next', '/'))