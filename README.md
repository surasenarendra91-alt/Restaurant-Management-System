# 🍴 Restaurant Management System (Django + REST API)

A complete backend + dashboard for running a restaurant: **menu, orders, tables, reservations, inventory**, with automatic stock deduction, table-availability checks, daily sales reports, low-stock alerts and an admin panel.

**Stack:** Python · Django 5/6 · Django REST Framework · SQLite · Vanilla JS dashboard

---

## ✅ Task Checklist

| Requirement | Where it is implemented |
|---|---|
| Set up backend (Django) | `restaurant_project/`, `restaurant/` |
| Database models (menu, orders, tables, reservations, inventory) | `restaurant/models.py` |
| APIs: place order, reserve table, update inventory, view menu | `restaurant/views.py`, `restaurant/urls.py` |
| Order processing logic | `services.place_order`, `services.update_order_status` |
| Table availability check | `services.is_table_free`, `services.find_available_tables` |
| Inventory auto-update | Stock is deducted inside `place_order` (restored on cancel) |
| **Optional:** daily sales report | `GET /api/reports/daily-sales/` |
| **Optional:** stock alerts | `GET /api/inventory/low-stock/` |
| **Optional:** admin access panel | `/admin/` (`restaurant/admin.py`) |
| Bonus: attractive dashboard UI | `restaurant/templates/restaurant/dashboard.html` |
| Bonus: automated tests | `restaurant/tests.py` (8 tests) |

---

## 🚀 Quick Start

```bash
# 1. (optional) create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. install dependencies
pip install -r requirements.txt

# 3. create the database
python manage.py migrate

# 4. load demo menu, recipes, tables, stock + admin user
python manage.py seed_data

# 5. run
python manage.py runserver
```

| URL | What |
|---|---|
| http://127.0.0.1:8000/ | 🎨 Dashboard (menu, cart, orders, tables, inventory, reports) |
| http://127.0.0.1:8000/api/ | Browsable REST API |
| http://127.0.0.1:8000/admin/ | Admin panel — **admin / admin123** |

Run the tests: `python manage.py test`

---

## 🗄️ Database Design

```
Category 1───* MenuItem 1───* RecipeItem *───1 Ingredient   (inventory)
                   │
                   └──* OrderItem *───1 Order *───0..1 Table 1───* Reservation
```

* **RecipeItem** links a dish to the ingredients one portion consumes — this is what powers inventory auto-update.
* **OrderItem.unit_price** stores a price snapshot, so old bills never change if the menu price changes.

---

## 🔌 API Reference

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/menu/?category=1&available=true&veg=true` | View menu |
| POST/PUT/DELETE | `/api/menu/` | Manage menu items |
| POST | `/api/orders/` | **Place order** |
| GET | `/api/orders/?status=placed` | List orders |
| POST | `/api/orders/<id>/status/` | Move order: placed → preparing → served → paid (or cancelled) |
| GET | `/api/tables/` | List tables |
| GET | `/api/tables/available/?date=2026-11-05&time=19:30&guests=4` | **Availability check** |
| POST | `/api/reservations/` | **Reserve a table** |
| POST | `/api/reservations/<id>/cancel/` | Cancel reservation |
| GET | `/api/inventory/` | View stock |
| POST | `/api/inventory/<id>/restock/` | **Update inventory** `{"quantity": 10}` |
| GET | `/api/inventory/low-stock/` | Stock alerts |
| GET | `/api/reports/daily-sales/?date=YYYY-MM-DD` | Daily sales + top items |

### Example: place an order
```http
POST /api/orders/
{
  "table": 1,
  "customer_name": "Rahul",
  "items": [
    {"menu_item": 1, "quantity": 2},
    {"menu_item": 4, "quantity": 1}
  ]
}
```
Response `201`: order with items, price snapshot and total.
Response `400` if stock is insufficient, e.g. `{"error": "Insufficient stock: Paneer (need 3.00, have 2.50 kg)"}`.

### Example: reserve a table
```http
POST /api/reservations/
{
  "table": 3, "customer_name": "Priya", "phone": "9876543210",
  "guests": 4, "date": "2026-11-05", "start_time": "20:00", "duration_minutes": 90
}
```

---

## 🧠 How the Core Logic Works

### 1. Order processing (`services.place_order`)
1. Check every dish is available.
2. Calculate total ingredients needed = Σ (recipe qty × order qty).
3. Lock inventory rows and verify stock is sufficient — **all-or-nothing**.
4. Deduct stock (**inventory auto-update**).
5. Save order + items with price snapshot and total.
6. Mark the table *occupied*.

All of this runs inside `transaction.atomic`, so a failed order never leaves half-updated stock.
Cancelling an order **restores** the ingredients and frees the table.

### 2. Table availability (`services.is_table_free`)
Two bookings clash when `new_start < existing_end AND existing_start < new_end`.
Back-to-back bookings (one ends 20:30, next starts 20:30) are allowed.

### 3. Reports & alerts
* Daily sales: revenue, order count, cancelled count and top-5 dishes (cancelled orders excluded from revenue).
* Low stock: any ingredient where `stock_quantity <= reorder_level`.

---

## 📁 Project Structure

```
restaurant_management/
├── manage.py
├── requirements.txt
├── README.md
├── restaurant_project/        # Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py / asgi.py
└── restaurant/                # Main app
    ├── models.py              # DB models
    ├── services.py            # Business logic (orders, tables, inventory, reports)
    ├── serializers.py         # DRF serializers
    ├── views.py               # API endpoints + dashboard view
    ├── urls.py                # API routes
    ├── admin.py               # Admin panel config
    ├── tests.py               # Automated tests
    ├── migrations/
    ├── management/commands/seed_data.py   # Demo data loader
    └── templates/restaurant/dashboard.html  # Dashboard UI
```

---

## 🔒 Notes for Production
The API is open (no login) so the demo and Postman work instantly. Before deploying: set `DEBUG=False`, change `SECRET_KEY`, restrict `ALLOWED_HOSTS`, and switch DRF permissions to `IsAuthenticated` / token auth (at least for reports and inventory).

## 🚀 Future Improvements
Bill/invoice PDF, payment integration, role-based staff login (waiter / chef / manager), WebSocket live kitchen screen, PostgreSQL.
