# Pantry Helper — TP2

> **Tecnologias e Programação Web — Trabalho Prático 2**
> Conversão do Pantry Helper (TP1) para arquitetura desacoplada com **Angular 17 + Django REST Framework**.

---

## Overview

Pantry Helper is a household pantry-management web application that helps families track what they have, what's about to expire, and what they can cook with it. This TP2 version replaces the Django template frontend used in TP1 with a clean two-tier setup:

- **Backend:** Django REST Framework (DRF) — REST API
- **Frontend:** Angular 17 — Single Page Application (SPA)

The two layers are fully decoupled, communicate over HTTP/JSON, and are deployed independently.

## Live demo

| Layer    | URL                                            |
|----------|------------------------------------------------|
| Frontend | <https://pantry-helper.netlify.app>            |
| API root | <https://anawkua.pythonanywhere.com/api/>      |
| Admin    | <https://anawkua.pythonanywhere.com/admin/>    |

Log in with any of the demo accounts further down in this README (e.g. `demo_admin` / `demo1234`).


---

## Features

- **Authentication** — Register, login, logout with DRF Token Authentication; a public landing page is shown to anonymous visitors
- **Households** — Create and manage households, search for and invite members, assign roles
- **Role-based access** — `Viewer` / `Member` / `Inventory Manager` / `Household Admin`
- **Pantry Management** — Add, edit, consume, waste, and delete pantry items (partial consume/waste supported)
- **Expiry Tracking** — Visual alerts for items expiring soon or already expired
- **Category Filtering & Search** — Filter by category, status, expiring soon, expired, plus full-text search
- **Recipe Management** — Create, browse, and view recipes with ingredients; ~500 preloaded recipes
- **Recipe Suggestions** — Recipes scored against the available pantry, ranked by missing-ingredient count
- **Activity Log** — Per-household history of add / update / consume / waste / delete actions
- **Dashboard** — Stats overview + expiring items + expired items + suggested recipes at a glance

---

## Project Structure

```
Pantry_Helper_Angular/
├── backend/                              # Django REST Framework
│   ├── manage.py
│   ├── requirements.txt
│   ├── pantry_api/                       # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── api/                              # Main app
│       ├── models.py                     # Household, PantryItem, Recipe, ItemLog, ...
│       ├── serializers.py
│       ├── views.py                      # ViewSets + Auth views
│       ├── urls.py
│       ├── permissions.py                # Role-based permissions
│       ├── admin.py
│       ├── fixtures/
│       │   └── wasteless_recipes_500.json
│       └── management/commands/
│           ├── load_demo_data.py
│           └── load_recipes_from_json.py
│
└── frontend/                             # Angular 17
    ├── angular.json
    ├── package.json
    ├── tsconfig.json
    └── src/
        ├── styles.css                    # Global styles (CSS variables)
        ├── index.html
        ├── main.ts
        ├── environments/
        │   ├── environment.ts
        │   └── environment.prod.ts
        └── app/
            ├── app.module.ts
            ├── app-routing.module.ts
            ├── models/models.ts          # TypeScript interfaces
            ├── services/                 # AuthService + interceptor, Household / Pantry / Recipe services
            ├── guards/auth.guard.ts      # AuthGuard, GuestGuard
            └── components/
                ├── landing/              # Public landing page
                ├── nav/
                ├── auth/                 # login, register, profile
                ├── dashboard/
                ├── household/            # list, detail, form
                ├── pantry/               # list, item-form
                └── recipes/              # list, detail, form
```

---

## Tech Stack

**Backend** — Python 3.10+, Django 4.2, Django REST Framework 3.14, django-cors-headers, SQLite (dev), `rest_framework.authtoken` for Token Authentication.

**Frontend** — Angular 17, TypeScript 5.2, RxJS, Angular HttpClient (with a custom `AuthInterceptor`), Reactive Forms, Angular Router with Route Guards.

---

## Setup — Backend

### Requirements
- Python 3.10+

### 1. Create a virtual environment
```bash
cd backend
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Apply migrations
```bash
python manage.py migrate
```

### 4. Load demo data (optional, recommended)
```bash
python manage.py load_recipes_from_json     # ~500 preloaded public recipes
python manage.py load_demo_data             # 4 demo users + household + items
```

Demo accounts (all share the password `demo1234`):

| Username       | Password   | Role               |
|----------------|------------|--------------------|
| `demo_admin`   | `demo1234` | Household Admin    |
| `demo_manager` | `demo1234` | Inventory Manager  |
| `demo_member`  | `demo1234` | Member             |
| `demo_viewer`  | `demo1234` | Viewer             |

### 5. (Optional) Create a Django superuser for the admin panel
```bash
python manage.py createsuperuser
```

### 6. Run the development server
```bash
python manage.py runserver
```

- API:        <http://127.0.0.1:8000/api/>
- Admin:      <http://127.0.0.1:8000/admin/>

---

## Setup — Frontend

### Requirements
- Node.js 18+
- Angular CLI 17 (`npm install -g @angular/cli`)

### 1. Install dependencies
```bash
cd frontend
npm install
```

### 2. Run the dev server
```bash
ng serve
```

The app is served at <http://localhost:4200>. **The backend must be running** at `http://127.0.0.1:8000`.

---

## REST API Endpoints

All endpoints require Token Authentication except `register` and `login`. Pass the token as `Authorization: Token <token>` on every authenticated request — the Angular `AuthInterceptor` does this automatically.

### Authentication

| Method        | Endpoint                  | Description                          | Auth |
|---------------|---------------------------|--------------------------------------|------|
| POST          | `/api/auth/register/`     | Register new user                    | No   |
| POST          | `/api/auth/login/`        | Login, returns a token               | No   |
| POST          | `/api/auth/logout/`       | Logout (invalidate token)            | Yes  |
| GET / PATCH   | `/api/auth/profile/`      | Get / update current profile         | Yes  |
| GET           | `/api/auth/search-user/`  | Look up a user by username           | Yes  |

### Households

| Method               | Endpoint                                | Description              | Auth          |
|----------------------|-----------------------------------------|--------------------------|---------------|
| GET / POST           | `/api/households/`                      | List / create            | Yes           |
| GET / PATCH / DELETE | `/api/households/{id}/`                 | Detail / edit / delete   | Yes / Admin   |
| GET / POST           | `/api/households/{id}/members/`         | List / add members       | Yes / Admin   |
| PATCH / DELETE       | `/api/households/{id}/members/{mid}/`   | Update / remove member   | Admin         |
| GET                  | `/api/households/{id}/stats/`           | Household statistics     | Yes           |

### Pantry items

| Method               | Endpoint                              | Description                | Auth                 |
|----------------------|---------------------------------------|----------------------------|----------------------|
| GET / POST           | `/api/pantry-items/`                  | List / create items        | Yes / Inv. Manager+  |
| GET / PATCH / DELETE | `/api/pantry-items/{id}/`             | Detail / edit / delete     | Yes / Inv. Manager+  |
| POST                 | `/api/pantry-items/{id}/consume/`     | Register consumption       | Member+              |
| POST                 | `/api/pantry-items/{id}/waste/`       | Register waste             | Member+              |

**Query parameters:** `household_id`, `status`, `category_id`, `search`, `expiring_soon`, `expired`, `ordering`.

Example: `/api/pantry-items/?household_id=1&status=available&search=milk&expiring_soon=true`

### Recipes, categories, logs

| Method               | Endpoint                  | Description                          | Auth |
|----------------------|---------------------------|--------------------------------------|------|
| GET / POST           | `/api/recipes/`           | List / create recipes                | Yes  |
| GET / PATCH / DELETE | `/api/recipes/{id}/`      | Detail / edit / delete               | Yes  |
| GET                  | `/api/recipes/suggested/` | Recipes matched against the pantry   | Yes  |
| GET                  | `/api/categories/`        | List food categories                 | Yes  |
| GET                  | `/api/logs/`              | Activity log for a household         | Yes  |

`/api/recipes/?household_id=1&search=pasta` returns recipes annotated with `can_make`, `missing_ingredients_count` and `available_ingredient_names` for that household.

---

## Authentication

The API uses **DRF Token Authentication**.

1. `POST /api/auth/register/` or `POST /api/auth/login/` → response contains `{ "token": "...", "user": {...} }`.
2. All subsequent requests include `Authorization: Token <token>`.
3. On the frontend, `AuthService` stores the token in `localStorage`. `AuthInterceptor` attaches it to every outgoing request and clears the session + redirects to `/login` if a 401 ever comes back.

---

## Role Permissions

| Action                        | Viewer | Member | Inv. Manager | Admin |
|-------------------------------|:------:|:------:|:------------:|:-----:|
| View pantry items             |   ✅   |   ✅   |      ✅      |   ✅  |
| Add / edit / delete items     |   ❌   |   ❌   |      ✅      |   ✅  |
| Consume / waste items         |   ❌   |   ✅   |      ✅      |   ✅  |
| Edit household                |   ❌   |   ❌   |      ❌      |   ✅  |
| Manage household members      |   ❌   |   ❌   |      ❌      |   ✅  |
| Delete household              |   ❌   |   ❌   |      ❌      |   ✅  |

`Member` can register what they consumed or wasted (so a younger family member can log their snacks) but cannot directly change the inventory — only `Inventory Manager` and `Admin` can add, edit, or delete items.

---

## Deployment

The two layers are deployed independently — a real n-tier setup as suggested in the assignment goals.

| Layer    | Host           | Live URL                                       | Plan |
|----------|----------------|------------------------------------------------|------|
| Backend  | PythonAnywhere | <https://anawkua.pythonanywhere.com/api/>      | Free |
| Frontend | Netlify        | <https://pantry-helper.netlify.app>            | Free |


### How it's wired

- **Backend (PythonAnywhere)** — Django + DRF served via WSGI on the
  free "Beginner" plan. Environment variables (`SECRET_KEY`, `DEBUG=False`,
  `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`) are set in the WSGI file. SQLite
  is used as the database; static files for the admin panel are served from
  `staticfiles/` via the Web tab's static-files mapping. CORS only allows
  the Netlify origin.
- **Frontend (Netlify)** — Static build of the Angular app, served from
  Netlify's global CDN. The build is auto-triggered on every push to
  `main`. `frontend/netlify.toml` configures the build command and the SPA
  fallback (so deep links like `/pantry` survive a page refresh). The
  production API URL is set in `src/environments/environment.prod.ts`.

