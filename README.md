# Okten

Каталог закладів і сервіс зустрічей **«Пиячок»** — веб-MVP за технічним завданням.

Пошук і фільтри, карта, відгуки, новини, ролі з модерацією, аналітика, внутрішній чат, вхід через email / Google / Facebook.

| Шар | Технології |
|-----|------------|
| Backend | Django, DRF, JWT, PostgreSQL або SQLite |
| Frontend | React, TypeScript, Vite, Leaflet |
| Інфра | Docker Compose, nginx |

---

## Можливості

**Каталог** — пошук, фільтри (тип, теги, особливості, рейтинг, чек), сортування (включно з віддаленістю), топ і топ-категорії, карта OSM, маршрут у Google Maps.

**Заклад** — фото, адреса, графік, контакти, клікабельні теги, новини, відгуки, чат з менеджером.

**Акаунт** — реєстрація / логін, профіль, улюблені, свої відгуки; перший запуск: 18+ і застереження про безпеку.

**Пиячок** — зустрічі (дата, час, мета, контакт, стать, компанія, хто платить, бюджет).

**Новини** — Загальні / Акції / Події (акції й події в каталозі лише з прапорцем `is_paid`).

**Менеджер** (`/manager`) — CRUD закладів і новин, Places-автозаповнення, модерація, статистика переглядів.

**Адмін** (`/admin`) — черга модерації, усі заклади й користувачі, відгуки, аналітика, CMS («Про нас», «Контакти», топ-категорії).

**Чат** — діалоги з менеджером закладу або автором пиячка.

---

## Ролі

| Роль | Логін у демо | Доступ |
|------|--------------|--------|
| `user` | `user_demo` | Каталог, відгуки, пиячок, чат |
| `venue_manager` | `manager_demo` | + «Мої заклади» |
| `critic` | `critic_demo` | + бейдж на відгуках |
| `super_admin` | `admin_demo` | + `/admin` |

Пароль для всіх демо: `DemoPass123!`

Скаргу на відгук подають лише **адмін** або **власник закладу**.  
Статуси закладу: `pending` → `published` / `rejected` / `archived`.

---

## Структура

```
├── backend/          Django API (apps: users, venues, reviews, favorites,
│                     news, hangout, messaging, analytics, common)
├── frontend/         React + Vite
├── infra/            docker-compose, nginx
├── scripts/          start-dev.ps1, start-dev-sqlite.ps1
└── README.md
```

---

## Запуск

### Швидко (SQLite, без Docker)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
```

У `backend/.env` додайте: `USE_SQLITE=1`

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py runserver
```

Другий термінал:

```powershell
cd frontend
npm install
npm run dev
```

Або однією командою підготовка БД: `.\scripts\start-dev-sqlite.ps1`

| Що | URL |
|----|-----|
| Сайт | http://localhost:5173 |
| Swagger | http://localhost:8000/api/docs/ |

Vite проксує `/api` і `/media` на backend.

### З PostgreSQL

Потрібен Docker Desktop.

```powershell
.\scripts\start-dev.ps1
```

Далі — `runserver` у `backend` і `npm run dev` у `frontend` (у `.env` має бути `POSTGRES_HOST=localhost`, без `USE_SQLITE`).

### Усе в Docker (як прод)

```powershell
cd infra
docker compose up --build
```

Сайт: http://localhost · Admin: http://localhost/admin/ · Docs: http://localhost/api/docs/

```powershell
docker compose exec backend python manage.py seed_demo
```

---

## Налаштування (`backend/.env`)

Зразок: [`backend/.env.example`](backend/.env.example). Файл `.env` з секретами не комітити.

| Змінна | Призначення |
|--------|-------------|
| `DJANGO_SECRET_KEY` | Секрет (на проді — обовʼязково свій) |
| `DJANGO_DEBUG` | `True` / `False` |
| `USE_SQLITE` | `1` — локально без Postgres |
| `POSTGRES_*` | База (якщо не SQLite) |
| `CORS_ALLOWED_ORIGINS` | Origins фронту |
| `GOOGLE_PLACES_API_KEY` | Автозаповнення адреси |
| `GOOGLE_OAUTH_CLIENT_ID` | Вхід через Google |
| `FACEBOOK_APP_ID` / `FACEBOOK_APP_SECRET` | Вхід через Facebook |

Без ключів Places/OAuth сайт працює; відповідні кнопки просто недоступні.

---

## OAuth

Фронт читає `GET /api/auth/oauth-config/`.

### Google

1. [Google Cloud Console](https://console.cloud.google.com/) → OAuth 2.0 Client ID (Web).
2. Origins: `http://localhost:5173`, `http://localhost` (і `https://localhost:5173` для HTTPS-дев).
3. `GOOGLE_OAUTH_CLIENT_ID` у `.env` → перезапуск backend.

### Facebook

Meta блокує `FB.login` на звичайному **http** — локально потрібен HTTPS:

```powershell
cd frontend
$env:VITE_HTTPS="1"
npm run dev
```

Відкрийте `https://localhost:5173` і прийміть сертифікат браузера.

1. [developers.facebook.com](https://developers.facebook.com/) → App → **Facebook Login**.
2. Permissions: `public_profile` (і `email` за потреби; для Live без App Review часто достатньо профілю).
3. Login settings: Web OAuth + **JS SDK = Yes**, domains: `https://localhost:5173`, `localhost`.
4. Basic: Privacy Policy, Category, іконка 1024×1024, Data Deletion.
5. **Публікація → Live** — щоб входили всі (у Development лише ролі App).
6. Ключі в `.env`, перезапуск backend.

---

## Сторінки

| Шлях | Опис |
|------|------|
| `/` | Головна, топ, каталог, фільтри, карта |
| `/venues/:id` | Заклад |
| `/news`, `/news/:id` | Новини |
| `/hangout` | Пиячок |
| `/login`, `/register` | Вхід |
| `/profile` | Профіль і улюблені |
| `/messages` | Чати |
| `/manager` | Мої заклади |
| `/admin` | Адмін-панель |
| `/pages/:slug` | CMS |
| `/sitemap` | Карта сайту |

---

## API

Префікс `/api/`. Інтерактивна документація: `/api/docs/`.

Auth · users · venues · places · reviews · complaints · favorites · news · hangouts · conversations · analytics · pages · top-categories · health.

JWT: `Authorization: Bearer <access>`.

---

## Тести

```powershell
cd backend
$env:USE_SQLITE="1"
.\.venv\Scripts\python.exe manage.py test core.tests apps.messaging.tests apps.users.tests.test_oauth -v 1

cd ..\frontend
npm run build
```

CI: [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

---

## Обмеження MVP

- Немає входу через Google Play / App Store (це веб, не стор-апки).
- Преміум-новини — прапорець `is_paid`, без платіжки.
- Facebook для всіх — потрібен режим **Live** у Meta.
- Немає Playwright E2E (є API-тести й збірка фронту).

---

## Команди

```powershell
# Backend
cd backend
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py runserver

# Frontend
cd frontend
npm run dev
$env:VITE_HTTPS="1"; npm run dev   # для Facebook
```
