# Pantry Helper - TP2

> **Technologies and Web Programming - Practical Work 2**
> Angular + Django REST Framework conversion of Pantry Helper (TP1)

---

## Overview

Pantry Helper is a household pantry and recipe management web application. This TP2 version replaces the Django template-based frontend (TP1) with a decoupled architecture:

- **Backend:** Django 5 + Django REST Framework - REST API with Token Authentication
- **Frontend:** Angular 17 - Single Page Application (SPA)

---

## Features

| Feature | Details |
|---|---|
| Authentication | Register, login, logout - Token-based (DRF) |
| Households | Create households, invite members, assign roles |
| Role-based access | Viewer / Member / Inventory Manager / Household Admin |
| Pantry Management | Add, edit, consume, waste, and delete pantry items |
| Expiry Tracking | Visual alerts for items expiring soon or already expired |
| Category Filtering | Organise items by food category |
| Recipe Management | Create, browse, and view recipes with ingredients |
| Recipe Suggestions | Recipes matched against your current pantry (sorted by fewest missing) |
| Ingredient Availability | ✅/❌ next to each ingredient when viewing a recipe |
| Partial Search | Search recipes by name, description, or partial ingredient name |
| Activity Log | View recent add/consume/waste actions per household |
| Dashboard | Stats, role summary, expiring / expired items, recipe suggestions |
| Landing Page | Public home page for unauthenticated visitors |
| 500 Preloaded Recipes | Loaded from fixture - read-only, available to all users |

---

## Role Permissions

| Action | Viewer | Member | Inv. Manager | Admin |
|---|:---:|:---:|:---:|:---:|
| View pantry items | ✅ | ✅ | ✅ | ✅ |
| View recipes | ✅ | ✅ | ✅ | ✅ |
| View suggested recipes | ✅ | ✅ | ✅ | ✅ |
| Mark items as consumed / wasted | ❌ | ✅ | ✅ | ✅ |
| Add / edit / delete pantry items | ❌ | ❌ | ✅ | ✅ |
| Create / edit / delete recipes | ❌ | ❌ | ❌ | ✅ |
| Edit household details | ❌ | ❌ | ❌ | ✅ |
| Add / remove / change member roles | ❌ | ❌ | ❌ | ✅ |

> **Notes:**
> - Any user can create a recipe; only the creator or a Household Admin can edit or delete it.
> - Preloaded recipes (`is_preloaded = True`) are read-only - nobody can edit or delete them.
> - `can_make` / missing-ingredient badges only appear when the household pantry has at least one item.

---

## Project Structure

```
pantry_helper_tp2/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── pantry_api/               # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── api/                      # Main app
│       ├── models.py             # Household, PantryItem, Recipe, …
│       ├── serializers.py        # DRF serializers (computed: can_make, missing_ingredients_count, available_ingredient_names)
│       ├── views.py              # ViewSets + Auth views
│       ├── urls.py
│       ├── permissions.py        # Role helpers: get_user_role, has_min_role
│       ├── migrations/
│       │   └── 0002_remove_low_status.py
│       └── management/commands/
│           ├── load_recipes_from_json.py   # loads 500 preloaded recipes
│           └── load_demo_data.py           # demo accounts + household
│
└── frontend/
    ├── angular.json
    ├── package.json
    └── src/
        ├── styles.css            # Global css
        ├── environments/
        └── app/
            ├── app.module.ts
            ├── app-routing.module.ts
            ├── models/           # TypeScript interfaces
            ├── services/         # Auth, Household, Pantry, Recipe
            ├── guards/           # AuthGuard, GuestGuard
            └── components/
                ├── landing/      # Public home page
                ├── nav/
                ├── auth/         # login, register, profile
                ├── dashboard/
                ├── household/    # list, detail
                ├── pantry/       # list, item-form
                └── recipes/      # list, detail, form
```

---

## Setup - Backend

### Requirements
- Python 3.10+

### 1. Create virtual environment

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

### 4. Load preloaded recipes (optional but recommended)

```bash
python manage.py load_recipes_from_json
```

Loads 500 public, read-only recipes from `api/fixtures/wasteless_recipes_500.json`.

### 5. Load demo accounts (optional)

```bash
python manage.py load_demo_data
```

Creates 4 demo users sharing a "Demo Household" with pantry items and recipes:

| Username | Password | Role |
|---|---|---|
| demo_admin | demo1234 | Household Admin |
| demo_manager | demo1234 | Inventory Manager |
| demo_member | demo1234 | Member |
| demo_viewer | demo1234 | Viewer |

### 6. Create superuser (optional)

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

- API: **http://127.0.0.1:8000/api/**
- Admin panel: **http://127.0.0.1:8000/admin/**

---

## Setup - Frontend

### Requirements
- Node.js 18+
- Angular CLI 17+

```bash
npm install -g @angular/cli
```

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Run the dev server

```bash
ng serve
```

App available at: **http://localhost:4200**

> Make sure the Django backend is running at `http://127.0.0.1:8000`.

---

## REST API Reference

### Auth

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/auth/register/` | Register new user | ❌ |
| POST | `/api/auth/login/` | Login, receive token | ❌ |
| POST | `/api/auth/logout/` | Logout, delete token | ✅ |
| GET / PATCH | `/api/auth/profile/` | View / update own profile | ✅ |
| GET | `/api/auth/search-user/?username=` | Find user by username | ✅ |

### Households

| Method | Endpoint | Description | Min role |
|---|---|---|---|
| GET / POST | `/api/households/` | List / create | Member |
| GET | `/api/households/{id}/` | Detail | Member |
| PATCH / DELETE | `/api/households/{id}/` | Edit / delete | Admin |
| GET | `/api/households/{id}/stats/` | Pantry statistics | Member |
| GET / POST | `/api/households/{id}/members/` | List / add members | Admin (write) |
| PATCH / DELETE | `/api/households/{id}/members/{mid}/` | Change role / remove | Admin |

### Pantry Items

| Method | Endpoint | Description | Min role |
|---|---|---|---|
| GET | `/api/pantry-items/` | List (filterable) | Viewer |
| POST | `/api/pantry-items/` | Create item | Inv. Manager |
| GET / PATCH / DELETE | `/api/pantry-items/{id}/` | Detail / edit / delete | Inv. Manager (write) |
| POST | `/api/pantry-items/{id}/consume/` | Consume quantity | Member |
| POST | `/api/pantry-items/{id}/waste/` | Mark as wasted | Member |

**Query parameters:** `household_id`, `status`, `category_id`, `search`, `expiring_soon=true`, `expired=true`, `ordering`

### Recipes

| Method | Endpoint | Description | Min role |
|---|---|---|---|
| GET | `/api/recipes/` | List (filterable, paginated) | Viewer |
| POST | `/api/recipes/` | Create recipe | Any authenticated |
| GET | `/api/recipes/{id}/` | Detail | Viewer |
| PATCH / DELETE | `/api/recipes/{id}/` | Edit / delete | Creator or Admin |
| GET | `/api/recipes/suggested/?household_id=` | Pantry-matched suggestions | Viewer |

**Query parameters:** `household_id` (enables `can_make`, `missing_ingredients_count`, `available_ingredient_names`), `search`

### Other

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/categories/` | List categories | ✅ |
| GET | `/api/logs/?household_id=` | Activity log | ✅ |

---

## Authentication

The API uses **Token Authentication** (DRF).

1. Register or login : receive `{ token, user }`
2. All subsequent requests include: `Authorization: Token <token>`
3. The Angular `AuthInterceptor` attaches the token automatically to every request

---

## Key Design Decisions

- **Recipes are global** - any user can create; only the creator or a Household Admin can edit/delete. Preloaded recipes (`is_preloaded=True`, `created_by=None`) are read-only to everyone.
- **`can_make` / missing count only when pantry has items** - badges are suppressed (`null`) when the household pantry is empty to avoid misleading "Missing N" labels for new users.
- **Pantry status** - only `available`, `consumed`, `wasted`. The `low` status was removed (migration 0002 converts existing data).
- **Recipe pagination** - `RecipePagination(page_size=1000)` to serve all 500 preloaded recipes in one request.
- **Partial recipe search** - implemented via manual `Q` objects (name, description, ingredient subquery) instead of DRF `SearchFilter` to avoid JOIN-duplication issues in SQLite.
- **Pantry map caching** - `_get_pantry_map` caches per-request in the serializer context to avoid N+1 queries when rendering a list of recipes.

---

## Deployment

### Backend - PythonAnywhere

1. Upload `backend/` to PythonAnywhere
2. Create a virtual environment and install `requirements.txt`
3. Set up a WSGI app pointing to `pantry_api.wsgi`
4. In `settings.py`:
   - Update `ALLOWED_HOSTS` with your PythonAnywhere domain
   - Set `DEBUG = False`
   - Set a secure `SECRET_KEY`
   - Set `CORS_ALLOW_ALL_ORIGINS = False` and add your frontend URL to `CORS_ALLOWED_ORIGINS`

### Frontend - Netlify / Vercel / Heroku

1. Update `src/environments/environment.prod.ts` with your PythonAnywhere API URL
2. Build for production:
   ```bash
   ng build --configuration production
   ```
3. Deploy `dist/pantry-helper/` to your chosen host
