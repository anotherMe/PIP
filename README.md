# Personal Investment Portfolio (PIP)

## Architecture
- **Backend**: FastAPI (Python) serving a REST JSON API, backed by SQLAlchemy and SQLite.
- **Frontend**: AlpineJS (HTML/JS)
---

## How to Run

### 1. Backend

The backend uses Python 3 and a virtual environment.

**Setup (First Time Only):**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Run the Server:**
```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```
The API will be accessible at `http://localhost:8000`. You can view the interactive API documentation at `http://localhost:8000/docs`.

### 2. Frontend

The frontend is completely static and uses Alpine.js via CDN. There is no `npm` or Node.js setup required.

**Run the Server:**
You can use Python's built-in HTTP server to serve the frontend files locally.

```bash
cd frontend
python3 -m http.server 8080
```
Open your browser and navigate to `http://localhost:8080`.
