# 🍲 Foodgram

Foodgram — это социальная сеть для любителей вкусно поесть. На платформе можно публиковать свои рецепты, изучать чужие и
даже генерировать список покупок для приготовления понравившихся блюд.

Проект построен на Django, Django REST Framework и React.

## 🚀 Локальный запуск проекта

### 📦 Клонирование репозитория

```bash
git clone https://github.com/Remsely/foodgram-st.git
```

```bash
cd foodgram-st
```

### ⚙️ Добавление .env файла (опционально)

```bash
nano .env
```

Пример содержимого файла:

```dotenv
SECRET_KEY=django-insecure-dev-super-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram
POSTGRES_PASSWORD=foodgram_1234
DB_HOST=db
DB_PORT=5432
```

### 🐳 Запуск проекта с Docker

**Вариант 1:** Локальная сборка и запуск

```bash
docker-compose up -d
```

**Вариант 2:** Запуск готовых образов из Docker Hub

```bash
docker-compose -f docker-compose.production.yml up -d
```

### 🌐 Что доступно после запуска

| URL                          | Описание                 |
|------------------------------|--------------------------|
| `http://localhost/admin/`    | Админ-панель Django      |
| `http://localhost/api/`      | API серверной части      |
| `http://localhost/api/docs/` | Документация API (Redoc) |
