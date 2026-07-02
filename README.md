# Clinic Network API

Базовый Django REST API для сети медицинских центров.

## Быстрый старт

1. Создайте виртуальное окружение и установите зависимости:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Выполните миграции:
   ```bash
   python manage.py migrate
   ```
3. Запустите сервер:
   ```bash
   python manage.py runserver
   ```

## Документация API

- Swagger: /api/v1/swagger/
- Redoc: /api/v1/redoc/
- Schema: /api/v1/schema/

## Основные возможности

- каталоги клиник, врачей и услуг;
- фильтрация врачей по клинике и специальности;
- фильтрация услуг по клинике и направлению;
- запись на приём с проверкой занятых слотов;
- просмотр истории записей пациента;
- базовая регистрация пользователя и профиль.
