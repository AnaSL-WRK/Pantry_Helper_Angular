# Pantry Helper - TP2

> **Technologies and Web Programming - Practical Work 2**
> Angular + Django REST Framework conversion of Pantry Helper (TP1)

---

## Overview

Pantry Helper is a household pantry management web application. This TP2 version replaces the Django template-based frontend (TP1) with:

- **Backend:** Django REST Framework (DRF) - REST API
- **Frontend:** Angular 17 - Single Page Application (SPA)

---

## Features

- **Authentication** - Register, login, logout with Token Authentication
- **Households** - Create and manage households; invite members with roles
- **Role-based access** - Viewer / Member / Inventory Manager / Household Admin
- **Pantry Management** - Add, edit, consume, waste and delete pantry items
- **Expiry Tracking** - Visual alerts for items expiring soon or already expired
- **Category Filtering** - Organise items by food category
- **Recipe Management** - Create, browse, and view recipes with ingredients
- **Recipe Suggestions** - Recipes matched against currently available pantry items
- **Activity Log** - View recent add/consume/waste actions per household
- **Dashboard** - Stats overview + expiring items + suggested recipes at a glance

---

## Project Structure

```
pantry_helper_tp2/
├── backend/                  # Django REST Framework
│   ├── manage.py
│   ├── requirements.txt
│   ├── pantry_api/           # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── api/                  # Main app
│       ├── models.py         # Household, PantryItem, Recipe, ...
│       ├── serializers.py
│       ├── views.py          # ViewSets + Auth views
│       ├── urls.py
│       ├── permissions.py    # Role-based permissions
│       └── management/
│           └── commands/
│               └── load_demo_data.py
│
└── frontend/                 # Angular 17
    ├── angular.json
    ├── package.json
    ├── tsconfig.json
    └── src/
        ├── styles.css        # Global styles
        ├── environments/
        │   └── environment.ts
        └── app/
            ├── app.module.ts
            ├── app-routing.module.ts
            ├── models/       # TypeScript interfaces
            ├── services/     # AuthService, HouseholdService, PantryService, RecipeService
            ├── guards/       # AuthGuard, GuestGuard
            └── components/
                ├── nav/
                ├── auth/     (login, register, profile)
                ├── dashboard/
                ├── household/ (list, detail, form)
                ├── pantry/    (list, item-form)
                └── recipes/   (list, detail, form)
```

---

## Setup - Backend

### Requirements
- Python 3.10+

### 1. Create virtual environment

```bash
cd backend
python -m venv venv
source venv/bin/activate        # macOS/Linux
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

### 4. Load demo data (optional)

```bash
python manage.py load_recipes_from_json
python manage.py load_demo_data
```

This creates 4 demo users, a household, pantry items, and recipes.

| Username       | Password   | Role               |
|----------------|------------|--------------------|
| demo_admin     | demo1234   | Household Admin    |
| demo_manager   | demo1234   | Inventory Manager  |
| demo_member    | demo1234   | Member             |
| demo_viewer    | demo1234   | Viewer             |


### 5. Create superuser (optional)

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

API available at: **http://127.0.0.1:8000/api/**
Admin panel: **http://127.0.0.1:8000/admin/**

---

## Setup - Frontend

### Requirements
- Node.js 18+
- Angular CLI 17

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

> Make sure the Django backend is running at `http://127.0.0.1:8000`

---

## REST API Endpoints

| Method | Endpoint                              | Description                    | Auth Required |
|--------|---------------------------------------|--------------------------------|---------------|
| POST   | `/api/auth/register/`                 | Register new user              | No            |
| POST   | `/api/auth/login/`                    | Login, get token               | No            |
| POST   | `/api/auth/logout/`                   | Logout                         | Yes           |
| GET/PATCH | `/api/auth/profile/`              | View/update profile            | Yes           |
| GET/POST | `/api/households/`                 | List / create households       | Yes           |
| GET/PATCH/DELETE | `/api/households/{id}/`   | Detail / edit / delete         | Yes           |
| GET/POST | `/api/households/{id}/members/`    | List / add members             | Yes           |
| PATCH/DELETE | `/api/households/{id}/members/{id}/` | Update / remove member   | Yes (Admin)   |
| GET    | `/api/households/{id}/stats/`         | Household statistics           | Yes           |
| GET/POST | `/api/pantry-items/`               | List / create pantry items     | Yes           |
| GET/PATCH/DELETE | `/api/pantry-items/{id}/` | Detail / edit / delete        | Yes           |
| POST   | `/api/pantry-items/{id}/consume/`     | Mark quantity consumed         | Yes (Inv.Mgr) |
| POST   | `/api/pantry-items/{id}/waste/`       | Mark quantity wasted           | Yes (Inv.Mgr) |
| GET/POST | `/api/recipes/`                    | List / create recipes          | Yes           |
| GET/PATCH/DELETE | `/api/recipes/{id}/`      | Detail / edit / delete         | Yes           |
| GET    | `/api/recipes/suggested/`             | Recipes matched to pantry      | Yes           |
| GET    | `/api/categories/`                    | List categories                | Yes           |
| GET    | `/api/logs/`                          | Activity log                   | Yes           |

**Query Parameters:**
- `/api/pantry-items/?household_id=1&status=available&search=milk&expiring_soon=true`
- `/api/recipes/?household_id=1&search=pasta`

---

## Deployment

### Backend - PythonAnywhere

1. Upload the `backend/` folder to PythonAnywhere
2. Create a virtual environment and install `requirements.txt`
3. Set up a WSGI app pointing to `pantry_api.wsgi`
4. In `settings.py`, update `ALLOWED_HOSTS` with your PythonAnywhere domain
5. Update `CORS_ALLOW_ALL_ORIGINS = False` and add your Heroku frontend URL to `CORS_ALLOWED_ORIGINS`
6. Set `DEBUG = False` and change `SECRET_KEY` to a secure value

### Frontend - Heroku (or Netlify / Vercel)

1. Update `src/environments/environment.prod.ts` with your PythonAnywhere API URL
2. Build for production:
   ```bash
   ng build --configuration production
   ```
3. Deploy `dist/pantry-helper/` to your chosen host

---

## Authentication

The API uses **Token Authentication** (Django REST Framework).

1. Register or login → receive a token
2. All subsequent requests include: `Authorization: Token <token>`
3. The Angular `AuthInterceptor` attaches the token automatically

---

## Role Permissions

| Action                        | Viewer | Member | Inv. Manager | Admin |
|-------------------------------|--------|--------|--------------|-------|
| View pantry items             | ✅     | ✅     | ✅           | ✅    |
| Add / edit / delete items     | ❌     | ❌     | ✅           | ✅    |
| Consume / waste items         | ❌     | ❌     | ✅           | ✅    |
| Manage household members      | ❌     | ❌     | ❌           | ✅    |
| Delete household              | ❌     | ❌     | ❌           | ✅    |
