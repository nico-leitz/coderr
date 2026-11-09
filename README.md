# Coderr - Freelance Service Marketplace API

A comprehensive, high-performance REST API for a freelance service marketplace, built with Django and Django REST Framework (DRF).

## Overview

Coderr allows business users to publish tiered service offers (`basic`, `standard`, `premium`) and enables customers to place orders, track progress, and leave reviews. Designed with strict professional standards, high performance, and security in mind.

## Features

- **Token Authentication:** Secure access to all endpoints via DRF token authentication and role-based permissions (`customer`, `business`, and `staff`).
- **Profile Management:** Separate endpoints and serializers for managing customer and business user profiles.
- **Offer & Package Management:** Full CRUD operations for service offers featuring nested package details, search, ordering, pagination (`PageNumberPagination`), and advanced filtering via `django-filter`.
- **Order Management:** Secure order creation utilizing historical price snapshots from offer details, status updates (`in_progress`, `completed`, `cancelled`), and live order counters for business users.
- **Review System:** Customer rating system with built-in duplicate prevention per business profile.
- **Platform Statistics:** Aggregated `/api/base-info/` endpoint providing real-time platform metrics.
- **High Performance:** Heavily optimized database queries utilizing `select_related()`, `prefetch_related()`, and database annotations (`Min`, `Avg`) to completely eliminate N+1 query problems.
- **Robust Testing:** Comprehensive test suite achieving >95% test coverage.

## Technologies Used

- **Language:** Python 3.10+
- **Framework:** Django & Django REST Framework (DRF)
- **Filtering & Pagination:** django-filter
- **Database:** SQLite (Default, easily configurable)

## Project Structure

```text
Coderr_Project/
│
├── core/                  # Centralized Django settings and main URL routing
├── user_auth/             # Authentication and user profiles app
├── offers_app/            # Service offers and tiered packages app
├── orders_app/            # Order processing and snapshot management app
├── reviews_app/           # Customer reviews and rating app
├── coderr_app/            # Platform statistics and seed management command
└── requirements.txt       # Project dependencies
```

## Installation & Setup

*Note: On macOS and Linux, you may need to use python3 and pip3 instead of python and pip.*

1. **Clone the repository**
   ```bash
   git clone <YOUR-REPOSITORY-URL>
   cd Coderr_Project
   ```

2. **Create and activate a virtual environment**
   - **Windows (Command Prompt / PowerShell):**
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - **macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   *(Make sure `(venv)` appears at the beginning of your terminal line)*

3. **Install dependencies**
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

4. **Apply database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Seed the database with test data (Optional)**
   ```bash
   python manage.py seed_db
   ```
   *Test accounts created by the seed command:*
   - **Business User:** `max_business` | **Password:** `test1234!`
   - **Customer User:** `customer_jane` | **Password:** `test1234!`

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```
   The API is now running locally at `http://127.0.0.1:8000/api/`. Keep this terminal window open!

## Running Tests & Coverage

To run the automated test suite and check test coverage:

```bash
coverage run --source='user_auth,offers_app,orders_app,reviews_app,coderr_app' manage.py test
coverage report -m
```

## Core API Endpoints

### Authentication & Profiles
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/registration/` | Register a new customer or business user and receive a token |
| `POST` | `/api/login/` | Authenticate an existing user and return their token |
| `GET` / `PATCH` | `/api/profile/{pk}/` | Retrieve or partially update a user profile |
| `GET` | `/api/profiles/business/` | List all business user profiles |
| `GET` | `/api/profiles/customer/` | List all customer profiles |

### Offers & Packages
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/offers/` | List paginated offers (supports filtering, search & ordering) |
| `POST` | `/api/offers/` | Create a new offer with 3 package details (Business users only) |
| `GET` / `PATCH` / `DELETE` | `/api/offers/{id}/` | Retrieve, update, or delete a specific offer |
| `GET` | `/api/offerdetails/{id}/` | Retrieve a specific offer detail package by ID |

### Orders & Counters
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/orders/` | List orders related to the authenticated user |
| `POST` | `/api/orders/` | Create a new order from an OfferDetail ID (Customers only) |
| `PATCH` | `/api/orders/{id}/` | Update order status (Business partner only) |
| `DELETE` | `/api/orders/{id}/` | Delete a specific order (Staff admin only) |
| `GET` | `/api/order-count/{business_user_id}/` | Get active (`in_progress`) order count for a business user |
| `GET` | `/api/completed-order-count/{business_user_id}/` | Get completed order count for a business user |

### Reviews & Utilities
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/reviews/` | List reviews (supports filtering by business user or reviewer) |
| `POST` | `/api/reviews/` | Create a new review for a business user (Customers only) |
| `PATCH` / `DELETE` | `/api/reviews/{id}/` | Update or delete a review (Author only) |
| `GET` | `/api/base-info/` | Get aggregated platform statistics |