-- Скрипт инициализации PostgreSQL для проекта «Сеть клиник»
-- Выполните от имени суперпользователя postgres:
--   psql -U postgres -f scripts/init_db.sql

CREATE DATABASE clinic_network
    WITH ENCODING 'UTF8'
    LC_COLLATE = 'ru_RU.UTF-8'
    LC_CTYPE = 'ru_RU.UTF-8'
    TEMPLATE template0;

-- Пользователь (опционально, если не используете postgres)
-- CREATE USER clinic_user WITH PASSWORD 'your_password';
-- GRANT ALL PRIVILEGES ON DATABASE clinic_network TO clinic_user;

-- Таблицы создаются через Django-миграции:
--   python manage.py migrate
