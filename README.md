<div align="center">

# Coderr - Freelance Service Marketplace API

*A comprehensive, high-performance REST API for a freelance service marketplace, built with Django and Django REST Framework*

<br>

![Python](https://img.shields.io/badge/PYTHON-3.14%2B-007ec6?style=for-the-badge&labelColor=555555)
![Django](https://img.shields.io/badge/DJANGO-6.1-51a825?style=for-the-badge&labelColor=555555)
![DRF](https://img.shields.io/badge/DRF-3.15-e04343?style=for-the-badge&labelColor=555555)

</div>

---

## Overview

Coderr allows business users to publish tiered service offers (`basic`, `standard`, `premium`) and enables customers to place orders, track progress, and leave reviews. Designed with strict professional standards, high performance, and security in mind.

## Features

- **User Authentication:** Secure access to endpoints via token authentication and role-based permissions (`customer`, `business`, and `staff`)
- **Profile Management:** Separate endpoints and serializers for managing customer and business user profiles
- **Offer & Package Management:** Full CRUD operations for service offers featuring nested package details, search, ordering, pagination (`PageNumberPagination`), and filtering via `django-filter`
- **Order Management:** Snapshot-based order creation from offer details, status updates (`in_progress`, `completed`, `cancelled`), and live order counters for business users
- **Review System:** Customer rating system with built-in duplicate prevention per business profile
- **Platform Statistics:** Aggregated `/api/base-info/` endpoint providing real-time platform metrics
- **High Performance:** Heavily optimized database queries utilizing `select_related()`, `prefetch_related()`, `Min()`, and `Avg()` to eliminate N+1 query problems
- **Automated Testing:** Comprehensive TDD test suite achieving 99% test coverage

## Technologies Used

- **Language:** Python 3.12+ / 3.14+
- **Framework:** Django & Django REST Framework (DRF)
- **Filtering:** django-filter & django-cors-headers
- **Database:** SQLite (Default, easily configurable)

## Project Structure

```text
Coderr_Project/
│
├── core/                  # Centralized Django settings and main URL routing
├── user_auth/             # Authentication and user profiles app
│   └── api/               # API layer (views.py, serializers.py, urls.py, permissions.py)
├── offers_app/            # Service offers and tiered packages app
│   └── api/               # API layer (views.py, serializers.py, urls.py, permissions.py, filters.py, pagination.py)
├── orders_app/            # Order processing and snapshot management app
│   └── api/               # API layer (views.py, serializers.py, urls.py, permissions.py)
├── reviews_app/           # Customer reviews and rating app
│   └── api/               # API layer (views.py, serializers.py, urls.py, permissions.py, filters.py)
├── coderr_app/            # Platform statistics and seed_db management command
│   └── api/               # API layer (views.py, urls.py)
├── .env.example           # Environment variables template
└── requirements.txt       # Project dependencies
```

## Installation & Setup

*Note: On macOS and Linux, you may need to use `python3` and `pip3` instead of `python` and `pip`.*

### 1. Clone the repository
```bash
git clone https://github.com/nico-leitz/Coderr.git
cd Coderr
```

### 2. Create and activate a virtual environment
- **Windows (Command Prompt / PowerShell):**
  ```bash
  python -m venv .venv
  .venv\Scripts\activate
  ```
- **macOS / Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
*(Make sure `(.venv)` appears at the beginning of your terminal line)*

### 3. Install dependencies
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure environment variables (`.env`)
Copy the provided `.env.example` template to create your local `.env` file:
- **Windows:**
  ```bash
  copy .env.example .env
  ```
- **macOS / Linux:**
  ```bash
  cp .env.example .env
  ```
*(Optional) Generate a fresh, secure `SECRET_KEY` automatically:*
```bash
python -c "from django.core.management.utils import get_random_secret_key as k; open('.env', 'w').write('SECRET_KEY=' + chr(39) + k() + chr(39) + '\nDEBUG=True\n')"
```

### 5. Apply database migrations
```bash
python manage.py migrate
```

### 6. Seed the database with test data (Optional)
```bash
python manage.py seed_db
```
*Test accounts created by `seed_db`:*
- **Business User:** `max_business` | **Password:** `test1234!`
- **Customer User:** `customer_jane` | **Password:** `test1234!`

### 7. Start the development server
```bash
python manage.py runserver
```
The API is now running locally at `[http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)`. Keep this terminal window open!

## Running Tests & Coverage

To run the automated test suite and verify the >95% test coverage requirement:

```bash
coverage run --source='user_auth,offers_app,orders_app,reviews_app,coderr_app' manage.py test
coverage report -m
```

## Core API Endpoints

### Authentication & Profiles
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/registration/` | Register a new customer or business user and receive an auth token |
| `POST` | `/api/login/` | Authenticate a user and return their token and user ID |
| `GET` | `/api/profile/{pk}/` | Retrieve detailed profile information for a specific user |
| `PATCH` | `/api/profile/{pk}/` | Update own profile details (Profile owner only) |
| `GET` | `/api/profiles/business/` | List all business user profiles |
| `GET` | `/api/profiles/customer/` | List all customer user profiles |

### Offers & Packages
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/offers/` | List paginated offers (supports search, ordering, and filtering) |
| `POST` | `/api/offers/` | Create a new offer with 3 package details (Business users only) |
| `GET` | `/api/offers/{id}/` | Retrieve a specific offer with package detail links |
| `PATCH` | `/api/offers/{id}/` | Partially update an offer and its nested details (Owner only) |
| `DELETE` | `/api/offers/{id}/` | Delete a specific offer (Owner only) |
| `GET` | `/api/offerdetails/{id}/` | Retrieve full details of a specific offer package |

### Orders & Counters
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/orders/` | List all orders associated with the authenticated user |
| `POST` | `/api/orders/` | Create a new order based on an OfferDetail ID (Customers only) |
| `PATCH` | `/api/orders/{id}/` | Update the status of an order (Business partner only) |
| `DELETE` | `/api/orders/{id}/` | Delete a specific order (Staff/Admin users only) |
| `GET` | `/api/order-count/{business_user_id}/` | Get count of `in_progress` orders for a business user |
| `GET` | `/api/completed-order-count/{business_user_id}/` | Get count of `completed` orders for a business user |

### Reviews & Platform Info
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/reviews/` | List all reviews (filterable by `business_user_id` and `reviewer_id`) |
| `POST` | `/api/reviews/` | Submit a new review for a business user (Customers only, 1 per business) |
| `PATCH` | `/api/reviews/{id}/` | Update rating or description of a review (Review author only) |
| `DELETE` | `/api/reviews/{id}/` | Delete a specific review (Review author only) |
| `GET` | `/api/base-info/` | Retrieve aggregated platform statistics (reviews, ratings, offers) |