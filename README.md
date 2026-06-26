# Сеть клиник — Backend

## Быстрый запуск (Windows PowerShell)

```powershell
cd C:\Users\User\Desktop\clinic

# 1. Виртуальное окружение
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Зависимости
pip install -r requirements.txt

# 3. Конфиг
copy .env.example .env

# 4a. PostgreSQL через Docker (рекомендуется)
docker compose up -d

# 4b. ИЛИ SQLite без Docker — в .env добавьте: USE_SQLITE=True

# 5. БД + тестовые данные
python manage.py migrate
python manage.py seed_data

# 6. Сервер
python manage.py runserver
```

Откройте http://127.0.0.1:8000/

## API

- GET  `/api/clinics/`
- GET  `/api/doctors/?clinic_id=1&specialty=терапевт`
- GET  `/api/services/?clinic_id=1`
- GET  `/api/appointments/?patient_phone=+79001234567`
- POST `/api/appointments/`
- GET/PATCH/DELETE `/api/appointments/<id>/`

## Структура

```
clinics/
├── models.py
├── serializers.py
├── views.py
├── urls.py
└── admin.py
clinic_network/       — settings, корневые urls
```
