# Enlingo

Enlingo is a full-stack web app with:
- **Frontend:** Vue (Vite)
- **Backend:** Flask (Python)

## Project Structure

```

.
├── vue-frontend/     # Vue + Vite frontend
└── flask-backend/    # Flask backend

````

## Prerequisites

- **Node.js** (LTS recommended) + **npm**
- **Python 3.10+** (3.11/3.12 also fine)
- (Recommended) **virtualenv** or Python venv support

---

## Frontend Setup (Vue)

```bash
cd vue-frontend
npm install
npm run dev
````

This will start the Vue dev server. The terminal will show the local URL (usually something like `http://localhost:5173`).

---

## Backend Setup (Flask)

```bash
cd flask-backend

# create venv
python -m venv venv

# activate venv (macOS/Linux)
source venv/bin/activate

# install dependencies
pip install -r requirements.txt

# run server
python run.py
```

> If you’re on Windows (PowerShell), activation is usually:
>
> ```powershell
> .\venv\Scripts\Activate.ps1
> ```

---

## Development Notes

* Run **backend** and **frontend** in **separate terminals**.
* If your frontend calls the backend API during development, ensure the backend is running and that your frontend API base URL/proxy is configured correctly.

---

## Common Commands

### Deactivate virtual environment

```bash
deapyctivate
```

### Reinstall backend dependencies (fresh)

```bash
pip install -r requirements.txt --upgrade
```
