# Okten

Каталог закладів і сервіс зустрічей **«Пиячок»**.

| Шар | Технології |
|-----|------------|
| Backend | Django, DRF, JWT, хмарна PostgreSQL |
| Frontend | React, TypeScript, Vite, Leaflet |
| Інфра | Docker Compose, nginx |

---

## Запуск (єдиний спосіб для перевірки)

З **кореня** проєкту потрібен заповнений [`backend/.env`](backend/.env) з **хмарною** PostgreSQL:

```bash
docker compose up --build
```

| Що | URL |
|----|-----|
| Сайт | http://localhost |
| Admin | http://localhost/admin/ |
| Swagger | http://localhost/api/docs/ |
| Health | http://localhost/api/health/ |

Локальний контейнер Postgres **не** використовується — БД лише хмарна (`POSTGRES_*` у `.env`).

---

## Структура

```
├── docker-compose.yml
├── backend/
│   ├── configs/
│   │   ├── settings/     # base.py, local.py, production.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── apps/             # users, venues, … → views/, serializers/, services/
│   ├── core/
│   └── requirements.txt
├── frontend/
├── infra/nginx/
├── postman/
└── README.md
```

Settings: локально `configs.settings.local`, у Docker — `configs.settings.production`.

---

## Налаштування (`backend/.env`)

Зразок: [`backend/.env.example`](backend/.env.example). Файл `.env` з секретами **не** комітити.

| Змінна | Призначення |
|--------|-------------|
| `DJANGO_SECRET_KEY` | Секрет Django |
| `DJANGO_DEBUG` | `True` / `False` |
| `POSTGRES_HOST` / `DB` / `USER` / `PASSWORD` / `PORT` | Хмарна PostgreSQL |
| `POSTGRES_SSLMODE` | Зазвичай `require` для Neon/Supabase |
| `CORS_ALLOWED_ORIGINS` | Origins фронту |
| `GOOGLE_PLACES_API_KEY` | Автозаповнення адреси |
| `GOOGLE_OAUTH_CLIENT_ID` | Google login |
| `FACEBOOK_APP_ID` / `FACEBOOK_APP_SECRET` | Facebook login |

---

## Postman

Див. [`postman/README.md`](postman/README.md):

1. Імпорт `postman/Okten_API.postman_collection.json`
2. Імпорт `postman/Okten_Local.postman_environment.json`
3. Оберіть environment **Okten Local**
4. Register / Login — скрипти самі збережуть `access_token`

---

## Тести

```bash
cd backend
python manage.py test -v 1
```

CI: [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

---

## API

Префікс `/api/`. JWT: `Authorization: Bearer <access>`.

Auth · users · venues · places · reviews · complaints · favorites · news · hangouts · conversations · analytics · pages · top-categories · health.
