from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from clinics.models import (
    Appointment,
    Clinic,
    Doctor,
    DoctorScheduleSlot,
    Equipment,
    Patient,
    Promotion,
    Review,
    Service,
    ServiceCategory,
)

PHOTO_DOCTOR = '27d078fc5f910ac9b6a38deb4edd56162a412c8a.png'

DIRECTIONS = [
    {
        'name': 'Гинекология',
        'image': 'bd4b3cb5032c02f54b1f78de3cea6bf20051a4e9.png',
        'description': 'Диагностика и лечение женских заболеваний, ведение беременности, гинекологические осмотры и процедуры.',
    },
    {
        'name': 'Урология',
        'image': '22c3f69fdffb9bc698683f636f91cdf283d041c8.png',
        'description': 'Лечение заболеваний мочеполовой системы у мужчин и женщин, диагностика и профилактика.',
    },
    {
        'name': 'Отоларингология',
        'image': '502bb916bbef6deb3a300d0ad255a73e9ae14ad4.png',
        'description': 'Лечение заболеваний уха, горла и носа у взрослых и детей: от отита до храпа.',
    },
    {
        'name': 'Неврология',
        'image': '624e3afe49fa14ecb401da854cbd7b1fe46a0ca2.png',
        'description': 'Лечение головных болей, невралгий, остеохондроза, вегетососудистой дистонии.',
    },
    {
        'name': 'Кардиология',
        'image': '93286177d89ccda094e69ebf29f946ed976a2338.png',
        'description': 'Диагностика и лечение сердечно-сосудистых заболеваний, профилактика инфарктов.',
    },
    {
        'name': 'Терапия',
        'image': '5ae93ebaf26653b815270d0459b69df6f32d9d1a.png',
        'description': 'Комплексная диагностика и лечение общих заболеваний, наблюдение за состоянием здоровья.',
    },
    {
        'name': 'Педиатрия',
        'image': 'd95aa342a3c0080fabac015baab438f82e33f9ea.png',
        'description': 'Наблюдение за здоровьем детей с рождения, лечение детских заболеваний.',
    },
    {
        'name': 'Гастроэнтерология',
        'image': '96aabbfce2aacd91d686a22442a42c620f279abe.png',
        'description': 'Лечение заболеваний желудочно-кишечного тракта, диетотерапия.',
    },
    {
        'name': 'Эндокринология',
        'image': 'a8c721cc33044945f3679e850d2ec67d2d451c06.png',
        'description': 'Диагностика и лечение гормональных нарушений, сахарного диабета.',
    },
    {
        'name': 'Хирургия',
        'image': '56eaf111575885869dec19327a29aedba2213432.png',
        'description': 'Хирургическое лечение заболеваний, амбулаторные операции.',
    },
    {
        'name': 'Ревматология',
        'image': 'd42390c024a263eb9c6a707ffc051506aa558231.png',
        'description': 'Лечение заболеваний суставов, соединительной ткани и сосудов.',
    },
    {
        'name': 'Дерматология',
        'image': '3cfdfcf9be7a64b3a1cf35d2c9bb66e903f2e60f.png',
        'description': 'Диагностика и лечение кожных заболеваний, дерматоскопия.',
    },
]

DOCTORS = [
    ('Иванова', 'Мария', 'Гинеколог', 12, 'Врач высшей категории, кандидат медицинских наук.'),
    ('Смирнов', 'Алексей', 'Уролог', 9, 'Врач первой категории, опыт работы более 9 лет.'),
    ('Кузнецова', 'Елена', 'Отоларинголог', 15, 'Занимается лечением ЛОР-заболеваний у взрослых и детей.'),
    ('Петров', 'Иван', 'Невролог', 20, 'Врач высшей категории, автор научных публикаций.'),
    ('Соколова', 'Анна', 'Кардиолог', 14, 'Специалист по профилактике сердечно-сосудистых заболеваний.'),
    ('Волков', 'Дмитрий', 'Терапевт', 8, 'Ведёт приём взрослых пациентов, диагностика и лечение.'),
    ('Морозова', 'Ольга', 'Педиатр', 11, 'Наблюдение за здоровьем детей с первых дней жизни.'),
    ('Лебедев', 'Николай', 'Гастроэнтеролог', 10, 'Лечение заболеваний ЖКТ, функциональная диагностика.'),
    ('Павлова', 'Татьяна', 'Эндокринолог', 13, 'Диагностика и лечение сахарного диабета и щитовидной железы.'),
    ('Орлов', 'Сергей', 'Хирург', 17, 'Амбулаторная хирургия, малоинвазивные вмешательства.'),
    ('Фёдорова', 'Наталья', 'Ревматолог', 7, 'Лечение заболеваний суставов и соединительной ткани.'),
    ('Козлов', 'Артём', 'Дерматолог', 6, 'Дерматоскопия, лечение акне и хронических дерматозов.'),
]

SERVICES = [
    ('Гинекология', 'Первичный приём гинеколога', 1800, 30),
    ('Гинекология', 'УЗИ органов малого таза', 1600, 30),
    ('Урология', 'Первичный приём уролога', 1800, 30),
    ('Урология', 'УЗИ почек и мочевого пузыря', 1400, 30),
    ('Отоларингология', 'Первичный приём ЛОРа', 1700, 30),
    ('Отоларингология', 'Эндоскопия носа и горла', 2000, 30),
    ('Неврология', 'Первичный приём невролога', 1900, 40),
    ('Неврология', 'ЭЭГ головного мозга', 2500, 60),
    ('Кардиология', 'Первичный приём кардиолога', 2000, 40),
    ('Кардиология', 'ЭКГ с расшифровкой', 900, 20),
    ('Терапия', 'Первичный приём терапевта', 1500, 30),
    ('Терапия', 'Повторный приём терапевта', 1200, 20),
    ('Педиатрия', 'Первичный приём педиатра', 1600, 30),
    ('Педиатрия', 'Вакцинация', 800, 20),
    ('Гастроэнтерология', 'Первичный приём гастроэнтеролога', 1800, 30),
    ('Эндокринология', 'Первичный приём эндокринолога', 1800, 30),
    ('Хирургия', 'Первичный приём хирурга', 1700, 30),
    ('Ревматология', 'Первичный приём ревматолога', 1800, 30),
    ('Дерматология', 'Первичный приём дерматолога', 1600, 30),
    ('Дерматология', 'Дерматоскопия', 1200, 20),
]


class Command(BaseCommand):
    help = 'Заполняет базу демонстрационными данными сети клиник (идемпотентно)'

    def handle(self, *args, **options):
        if Clinic.objects.exists():
            self.stdout.write(self.style.WARNING('Данные уже существуют, добавляю только недостающее'))
            categories = {c.name: c for c in ServiceCategory.objects.all()}
            for item in DIRECTIONS:
                if item['name'] not in categories:
                    categories[item['name']] = ServiceCategory.objects.create(**item)
            self.stdout.write(self.style.SUCCESS('Недостающие направления добавлены'))
            return

        clinic1 = Clinic.objects.create(
            name='Клиника «МЕДСЕРВИС»',
            city='Томск',
            address='г. Томск, ул. 79 Гвардейской дивизии, 6',
            phone='8 (3822) 50-00-49',
            email='info@docnear.ru',
            description='Многопрофильный медицинский центр полного цикла.',
            working_hours='Пн–пт: 8.00–20.00, сб: 9.00–17.00, вс: 10.00–16.00',
        )
        clinic2 = Clinic.objects.create(
            name='Клиника «МЕДСЕРВИС» на Пушкина',
            city='Томск',
            address='г. Томск, ул. Пушкина, 43',
            phone='8 (3822) 50-00-49',
            email='info@docnear.ru',
            description='Филиал сети клиник в центре города.',
            is_branch=True,
            parent_clinic=clinic1,
            working_hours='Пн–пт: 8.00–20.00, сб: 9.00–17.00',
        )

        categories = {}
        for item in DIRECTIONS:
            categories[item['name']] = ServiceCategory.objects.create(**item)

        doctors = {}
        for idx, (last, first, specialty, experience, bio) in enumerate(DOCTORS):
            name_map = {
                'Гинеколог': 'Гинекология',
                'Уролог': 'Урология',
                'Отоларинголог': 'Отоларингология',
                'Невролог': 'Неврология',
                'Кардиолог': 'Кардиология',
                'Терапевт': 'Терапия',
                'Педиатр': 'Педиатрия',
                'Гастроэнтеролог': 'Гастроэнтерология',
                'Эндокринолог': 'Эндокринология',
                'Хирург': 'Хирургия',
                'Ревматолог': 'Ревматология',
                'Дерматолог': 'Дерматология',
            }
            clinic = clinic1 if idx % 3 != 2 else clinic2
            doctors[specialty] = Doctor.objects.create(
                clinic=clinic,
                category=categories[name_map[specialty]],
                first_name=first,
                last_name=last,
                specialty=specialty,
                phone=f'+7 982 {idx:03d}-{idx:02d}-{idx:02d}',
                photo=PHOTO_DOCTOR,
                bio=bio,
                qualification='Высшая квалификационная категория',
                experience_years=experience,
            )

        for category_name, name, price, duration in SERVICES:
            Service.objects.create(
                clinic=clinic1,
                category=categories[category_name],
                name=name,
                price=price,
                duration_minutes=duration,
                description=f'{name}. Консультация профильного специалиста клиники «МЕДСЕРВИС».',
            )

        promotions = [
            {
                'title': 'Скидка -20% на МРТ',
                'description': 'Пройти МРТ любого отдела позвоночника и суставов со скидкой 20% до конца месяца.',
                'valid_until': timezone.now().date() + timedelta(days=60),
                'image': '2cf9f4594d091cb8c094edd35e77a980b8f7187a.png',
                'color': '27c78a',
            },
            {
                'title': 'Бесплатная консультация невролога',
                'description': 'При записи на комплексное обследование позвоночника консультация невролога в подарок.',
                'valid_until': timezone.now().date() + timedelta(days=30),
                'image': 'bc751aada3dd438da4af22bbfba2f60b222d8fd7.png',
                'color': '6666f2',
            },
            {
                'title': 'УЗИ со скидкой 15%',
                'description': 'Скидка на все виды УЗИ-диагностики при предварительной записи через сайт.',
                'valid_until': timezone.now().date() + timedelta(days=45),
                'image': 'e012e560ae205e6da86f2a0007fa80bbcd3922c8.png',
                'color': 'f57575',
            },
            {
                'title': 'Чек-ап для всей семьи',
                'description': 'Комплексное обследование организма со скидкой 30%: анализы, УЗИ, консультации.',
                'valid_until': timezone.now().date() + timedelta(days=90),
                'image': '2cf9f4594d091cb8c094edd35e77a980b8f7187a.png',
                'color': 'ffdb5c',
            },
        ]
        for item in promotions:
            Promotion.objects.create(**item)

        equipment = [
            {'name': 'МРТ 1.5 Тл', 'description': 'Магнитно-резонансный томограф экспертного класса для диагностики головного мозга, позвоночника и суставов.'},
            {'name': 'Компьютерный томограф', 'description': 'КТ с низкой лучевой нагрузкой для исследования грудной клетки, брюшной полости и костей.'},
            {'name': 'Цифровой рентген', 'description': 'Современный рентген-аппарат с минимальной дозой облучения и мгновенным результатом.'},
            {'name': 'УЗИ экспертного класса', 'description': 'Аппараты УЗИ с высоким разрешением для диагностики внутренних органов и сосудов.'},
        ]
        for item in equipment:
            Equipment.objects.create(**item)

        patient = Patient.objects.create(
            first_name='Алексей',
            last_name='Смирнов',
            phone='+79001234567',
            email='alexey@example.com',
            birth_date=timezone.now().date() - timedelta(days=365 * 30),
        )

        reviews = [
            ('Анна Петрова', 'Очень внимательный и грамотный специалист. Всё подробно объяснила, назначила правильное лечение. Рекомендую!', 5, 'Невролог'),
            ('Ирина Соколова', 'Хожу в эту клинику уже несколько лет. Всегда чисто, вежливый персонал, врачи настоящие профессионалы.', 5, 'Терапевт'),
            ('Сергей Морозов', 'Быстро записали, без очередей. Доктор внимательно выслушал, провёл осмотр. Спасибо!', 4, 'Уролог'),
            ('Екатерина Дмитриева', 'Отличный гинеколог, всё аккуратно и деликатно. Никаких неприятных ощущений, рекомендую всем.', 5, 'Гинеколог'),
            ('Павел Громов', 'Хорошая клиника, но к приёму пришлось подождать минут 15. В остальном всё отлично.', 4, 'Кардиолог'),
            ('Ольга Лебедева', 'Лечили ребёнку у педиатра. Врач нашла подход, объяснила всё понятно. Очень благодарны!', 5, 'Педиатр'),
            ('Дмитрий Фёдоров', 'Прошёл обследование по программе. Всё организовано чётко, результаты выдали в тот же день.', 5, 'Гастроэнтеролог'),
            ('Мария Кузнецова', 'Кожа перестала беспокоить после курса лечения. Дерматолог настоящий профи. Спасибо клинике!', 5, 'Дерматолог'),
        ]
        for name, text, rating, specialty in reviews:
            doctor = doctors.get(specialty) or doctors['Терапевт']
            Review.objects.create(
                patient_name=name,
                text=text,
                rating=rating,
                doctor=doctor,
                created_at=timezone.now().date() - timedelta(days=len(reviews) * 7),
            )

        for idx, (specialty, doctor) in enumerate(doctors.items()):
            slot_start = timezone.now() + timedelta(days=3 + idx, hours=9)
            DoctorScheduleSlot.objects.create(
                doctor=doctor,
                start_at=slot_start,
                end_at=slot_start + timedelta(minutes=40),
            )

        Appointment.objects.create(
            patient=patient,
            doctor=doctors['Терапевт'],
            service=Service.objects.get(name='Первичный приём терапевта'),
            scheduled_at=timezone.now() + timedelta(days=5, hours=10),
            status=Appointment.Status.CONFIRMED,
            notes='Тестовая запись',
        )

        self.stdout.write(self.style.SUCCESS(
            f'Создано: {Clinic.objects.count()} клиник, '
            f'{ServiceCategory.objects.count()} направлений, '
            f'{Doctor.objects.count()} врачей, '
            f'{Service.objects.count()} услуг, '
            f'{Promotion.objects.count()} акций, '
            f'{Review.objects.count()} отзывов, '
            f'{Equipment.objects.count()} единиц оборудования',
        ))
