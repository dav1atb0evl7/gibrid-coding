# GIBRID X CODING Platform

A modular Telegram business platform for GIBRID X CODING: aiogram customer bot, FastAPI admin API, SQLite persistence, Alembic migrations and a React operations dashboard.

## Components

- `backend/app/bot`: Telegram routers, keyboards and per-user rate limiting.
- `backend/app/services`: order creation, validation, metrics and service catalog.
- `backend/app/models`: users, clients, orders, services, portfolio, admins, messages and notifications.
- `backend/app/admin`: bearer-protected dashboard API for metrics, orders and clients.
- `backend/app/ai`: Gemini integration boundary. It is intentionally not enabled; the fallback never promises a price.
- `backend/migrations`: versioned SQLite schema.
- `admin-dashboard`: responsive React dashboard for order triage.

The official company logo was not present in the supplied workspace. The dashboard uses a text GX wordmark until the official asset is added.

## Configure

1. Create a Telegram bot with BotFather and copy its token.
2. Copy `backend/.env.example` to `backend/.env` and set `BOT_TOKEN`, `DATABASE_URL`, `ADMIN_API_TOKEN`, and the numeric `ADMIN_TELEGRAM_IDS` (comma-separated for multiple admins). Use long, unique secrets; do not commit `.env`.
3. Set `CORS_ORIGINS` to the dashboard's origin and `VITE_API_URL` when building the dashboard to the backend URL reachable by administrators' browsers. The dashboard token is kept in `sessionStorage` and sent only as a bearer header.
4. For webhook deployment, set `BOT_MODE=webhook`, `WEBHOOK_BASE_URL` to the public HTTPS base URL, and a random `WEBHOOK_SECRET`. Polling is the default and requires no inbound Telegram webhook.

## Local development

Use Python 3.12+ and Node.js 20+. The bot stores data in `backend/gxc.db`; no separate database server is needed. Create a Python environment, install `backend/requirements.txt`, configure `backend/.env`, then run:

```powershell
Copy-Item backend/.env.example backend/.env
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

In another terminal:

```powershell
cd admin-dashboard
npm install
npm run dev
```

The example `DATABASE_URL=sqlite+aiosqlite:///./gxc.db` stores the SQLite file in the backend working directory. Keep the database file in backups and do not delete it when updating the application. Configure `CORS_ORIGINS=http://localhost:5173` and `VITE_API_URL=http://localhost:8000` for local dashboard use.

For VPS deployment, install Python 3.12+ and Node.js 20+ on the server. Run the Alembic migration, then start the API with a process manager such as systemd and serve the built dashboard through a web server. Persist and back up `backend/gxc.db`, terminate TLS at a reverse proxy, and do not expose the admin API over plain public HTTP. SQLite is a good fit for a single application instance; use a migration to PostgreSQL if the service later needs concurrent multi-instance writes.

## Admin access

`/admin` in Telegram and Telegram order notifications are restricted to IDs in `ADMIN_TELEGRAM_IDS`. The web API uses `Authorization: Bearer <ADMIN_API_TOKEN>` and exposes:

- `GET /api/admin/dashboard`
- `GET /api/admin/orders`
- `PATCH /api/admin/orders/{public_id}` for status, internal notes and staff assignment
- `GET /api/admin/clients`

Keep the API token separate from Telegram bot credentials. Rotate it if exposed. Failed authorization responses do not disclose configuration details.

## Data and integrations

Orders are only persisted after a client confirms the summary. IDs are allocated as `GXC-000001` and increase with the database order primary key. New orders notify configured Telegram admins. Dashboard metrics are database-backed. Add actual portfolio entries and the official logo before launch; the portfolio intentionally starts empty rather than claiming sample work as company work.

The architecture keeps CRM/API integration at the service layer. Gemini credentials and model settings are provisioned via environment variables, but no AI calls are made until an administrator explicitly enables and configures that integration. AI responses must remain informational; pricing must be confirmed by staff.

## Tests

From the repository root, with backend dependencies installed:

```powershell
$env:BOT_TOKEN='test-token'
$env:DATABASE_URL='sqlite+aiosqlite:///./test.db'
$env:ADMIN_API_TOKEN='test-secret'
python -m pytest backend/tests -q
```

For a new migration, create a revision under `backend/migrations/versions` and apply it with `alembic upgrade head` from `backend/`.
