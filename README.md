# 🔄 Real-Time Database Updates System

A backend system that pushes live database changes to connected clients — no polling required. Built with Python, FastAPI, PostgreSQL, and WebSockets.

---

## 📌 What This Does

Whenever a row is **inserted, updated, or deleted** in the `orders` table, every connected client is instantly notified with the new data — in real time.

```
PostgreSQL (trigger fires)
        ↓
    NOTIFY on 'orders_channel'
        ↓
  Python backend (asyncpg listens)
        ↓
  WebSocket broadcast
        ↓
  All connected clients receive the update
```

---

## 🧠 Approach & Design Decisions

### Why PostgreSQL LISTEN/NOTIFY?

The assignment explicitly rules out polling. There are a few ways to detect database changes without it:

| Approach | How it works | Why I didn't choose it |
|---|---|---|
| Polling | Client asks repeatedly | Explicitly ruled out |
| Change Data Capture (CDC) | Reads DB transaction logs (e.g. Debezium) | Overkill for this scope |
| **LISTEN/NOTIFY** | DB fires a notification, backend listens | ✅ Simple, built into PostgreSQL, efficient |

PostgreSQL has a native pub/sub mechanism. A **trigger** on the `orders` table fires `pg_notify()` on every change, and the Python backend listens on that channel using `asyncpg`. No external message broker needed.

### Why WebSockets?

Once the backend detects a DB change, it needs to push it to clients. WebSockets provide a persistent, bidirectional connection — perfect for real-time updates. The alternative (HTTP long-polling or SSE) would be less clean for this use case.

### Why FastAPI + asyncpg?

Both are async-native. The DB listener and the WebSocket server run concurrently in the same event loop without blocking each other — no threads, no complexity.

---

## 🗂️ Project Structure

```
realtime-db-updates/
├── backend/
│   ├── main.py        # FastAPI app + WebSocket endpoint
│   ├── db.py          # PostgreSQL LISTEN logic + client broadcasting
│   └── models.py      # Order data structure
├── client/
│   └── client.py      # Python WebSocket client
├── sql/
│   └── setup.sql      # Table + trigger setup
├── .env               # DB credentials (not committed)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Prerequisites

- Python 3.10+
- PostgreSQL (with pgAdmin or psql)
- Git

---

## 🚀 How to Run

### 1. Clone the repository

```bash
git clone https://github.com/your-username/realtime-db-updates.git
cd realtime-db-updates
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up the database

Open pgAdmin (or psql), create a database called `realtime_db`, then run the setup script:

```sql
-- Run this in your query tool against realtime_db
\i sql/setup.sql
```

This creates the `orders` table and attaches the change-notification trigger automatically.

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_NAME=realtime_db
```

### 6. Start the backend server

```bash
uvicorn backend.main:app --reload --reload-dir backend
```

You should see:

```
[Server] Started. DB listener running in background.
[DB] Listening for changes on 'orders_channel'...
```

### 7. Start the client (in a new terminal)

```bash
python client/client.py
```

You should see:

```
Connecting to server...
Connected! Waiting for order updates...
```

### 8. Trigger a change

Go to pgAdmin and run:

```sql
INSERT INTO orders (customer_name, product_name, status)
VALUES ('Sidharth', 'Mechanical Keyboard', 'pending');
```

The client terminal will instantly display:

```
--- Order Update Received ---
  Operation     : INSERT
  Order ID      : 1
  Customer      : Sidharth
  Product       : Mechanical Keyboard
  Status        : pending
  Updated At    : 2026-05-19T10:18:15.928603
-----------------------------
```
<img width="1874" height="672" alt="Sidharth Vijayan - apt submission" src="https://github.com/user-attachments/assets/aa05563f-7d5a-4803-872f-f62d4f5db914" />

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Database | PostgreSQL |
| DB Driver | asyncpg |
| Backend Framework | FastAPI |
| Server | Uvicorn |
| Real-time Transport | WebSockets |
| Client | Python (websockets library) |
| Config | python-dotenv |

---

## 📐 Scalability Considerations

- **Multiple clients** are supported out of the box — the backend maintains a set of connected WebSocket clients and broadcasts to all of them simultaneously.
- **Single DB connection** handles all notifications via `asyncpg`'s listener — no per-client DB connections needed.
- For higher scale, the WebSocket layer could be replaced with a message broker (e.g. Redis Pub/Sub) and the backend could run as multiple instances behind a load balancer.

---

## 📄 License

MIT
