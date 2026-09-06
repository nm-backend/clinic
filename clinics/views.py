from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from clinics.models import (
    CallbackRequest,
    Clinic,
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
    doctors = Doctor.objects.select_related('clinic', 'category').filter(
        is_active=True,
        clinic__is_active=True,
    )[:8]
    equipment = Equipment.objects.filter(is_active=True)
    context = {
        'categories': categories,
        'doctors': doctors,
        'equipment': equipment,
        'promotions': Promotion.objects.filter(is_active=True),
    }
    return render(request, 'index.html', context)


def directions(request):
    context = {'categories': ServiceCategory.objects.all()}
    return render(request, 'directions.html', context)


def direction_detail(request, slug):
    category = get_object_or_404(ServiceCategory, slug=slug)
    doctors = Doctor.objects.filter(
        category=category,
        is_active=True,
        clinic__is_active=True,
    )
    services = Service.objects.filter(category=category, is_active=True)
    reviews = Review.objects.filter(
        doctor__category=category,
        is_active=True,
    ).select_related('doctor')[:3]
    context = {
        'category': category,
        'doctors': doctors,
        'services': services,
        'reviews': reviews,
    }
    return render(request, 'direction_detail.html', context)


def doctors(request):
    queryset = Doctor.objects.select_related('clinic', 'category').filter(
        is_active=True,
        clinic__is_active=True,
    )
    category_slug = request.GET.get('category')
    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)
    search = request.GET.get('q', '').strip()
    if search:
        queryset = queryset.filter(
            Q(last_name__icontains=search)
            | Q(first_name__icontains=search)
            | Q(specialty__icontains=search),
        )
    context = {
        'doctors': queryset,
        'categories': ServiceCategory.objects.all(),
        'active_category': category_slug,
        'search': search,
    }
    return render(request, 'doctors.html', context)


def services(request):
    categories = ServiceCategory.objects.all()
    all_services = Service.objects.select_related('category', 'clinic').filter(is_active=True)
    grouped_services = [
        {'category': category, 'services': all_services.filter(category=category)}
        for category in categories
    ]
    context = {'grouped_services': grouped_services}
    return render(request, 'services.html', context)


def service_detail(request, pk):
    service = get_object_or_404(
        Service.objects.select_related('category', 'clinic'),
        pk=pk,
        is_active=True,
    )
    doctors = Doctor.objects.filter(
        category=service.category,
        is_active=True,
        clinic__is_active=True,
    )
    context = {'service': service, 'doctors': doctors}
    return render(request, 'service_detail.html', context)


def promotions(request):
    context = {'promotions': Promotion.objects.filter(is_active=True)}
    return render(request, 'promotions.html', context)


def about(request):
    context = {
        'reviews': Review.objects.filter(is_active=True)[:3],
    }
    return render(request, 'about.html', context)


def reviews(request):
    context = {'reviews': Review.objects.filter(is_active=True)}
    return render(request, 'reviews.html', context)


def contacts(request):
    doctors = Doctor.objects.filter(is_active=True, clinic__is_active=True)[:8]
    context = {'doctors': doctors}
    return render(request, 'contacts.html', context)


def oms(request):
    return render(request, 'oms.html')


def dms(request):
    return render(request, 'dms.html')


def analyses(request):
    return render(request, 'analyses.html')


def legal(request):
    return render(request, 'legal.html')


def appointment_page(request):
    return render(request, 'appointment.html')


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