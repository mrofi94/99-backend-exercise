# 🛍️ 99 Backend Exercise – Setup & Usage Guide

This project consists of 3 microservices:

- `listing_service` – Handles listing data
- `user_service` – Handles user data
- `public_api` – Gateway service that exposes public API

---

## 📦 Requirements

- Python 3.8+
- Docker & Docker Compose
- `pip`, `virtualenv` (for manual run)

---

## 🌐 API Collection

Postman Collection (organized by service):

👉 [Open Postman Collection](https://mrofiarofah.postman.co/workspace/New-Team-Workspace~b91e1aa3-b051-4d97-af31-7a00055c99e0/collection/403743-51d7f063-f257-43ac-813b-6322fd86b7a2?action=share\&creator=403743)

depending on how we run the project, postman collection below may not be accessible
1. listings
2. users

please check the "Environment Access" table below for different methods on running the project and how it would affect accessibility

---

## 🧲 Environment Access

| Service           | Manual Run | Docker Dev | Docker Prod |
| ----------------- | ---------- | ---------- | ----------- |
| `listing_service` | ✅ Yes      | ✅ Yes      | ❌ Hidden    |
| `user_service`    | ✅ Yes      | ✅ Yes      | ❌ Hidden    |
| `public_api`      | ✅ Yes      | ✅ Yes      | ✅ Yes       |

---

## ⚙️ 1. Manual Run (Dev Mode)

Each service reads from `.env.dev` and runs on custom ports.

```bash
# In each service folder (e.g. listing_service/)
python listing_service.py --port=6000 --debug=true

# Or for user_service/
python user_service.py --port=7000 --debug=true

# Or for public_api/
python public_api.py --port=8000 --debug=true
```

Make sure to have `.env.dev` in each service directory like:

```env
ENV=dev
LISTING_SERVICE_URL=http://localhost:6000/listings
USER_SERVICE_URL=http://localhost:7000/users
PORT=8000
DEBUG=true
```

---

## 🐳 2. Run with Docker (Dev Mode)

This exposes all 3 services:

- `listing_service`: [http://localhost:6000](http://localhost:6000)
- `user_service`: [http://localhost:7000](http://localhost:7000)
- `public_api`: [http://localhost:8000](http://localhost:8000)

### Step-by-step:

```bash
docker-compose -f docker-compose.dev.yml up --build
```

It will use `.env.dev` inside each service folder.

---

## 🔐 3. Run with Docker (Prod Mode)

This **only exposes **`` on port `8000`. The other services are internal-only.

```bash
docker-compose -f docker-compose.prod.yml up --build
```

It uses `.env.prod` for each service and enforces internal access.

---

## 🔄 Switching Environments

- `.env.dev`: used by manual run and Docker Dev
- `.env.prod`: used only by Docker Prod



