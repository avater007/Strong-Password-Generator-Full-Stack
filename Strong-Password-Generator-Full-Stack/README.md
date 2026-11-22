# Strong Password Generator (Full Stack)

A full-stack password generator with a React frontend and Flask REST API. It supports customizable passwords, strength estimation, copy-to-clipboard, and optional saved password history.

## Tech stack
- Frontend: React + Vite
- Backend: Python + Flask + Flask-CORS
- Database: SQLite by default (SQLAlchemy); MySQL can be configured with `DATABASE_URL`

> Security note: This is an educational project. The app does not encrypt saved passwords. Password history is disabled by default; only enable it for local demos and never store real passwords.

## Requirements
- Python 3.10+
- Node.js 18+

## 1. Start the backend
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
# macOS/Linux: cp .env.example .env
python app.py
```
The API runs at `http://localhost:5000`.

## 2. Start the frontend
Open a second terminal:
```bash
cd frontend
npm install
npm run dev
```
Open the URL printed by Vite (usually `http://localhost:5173`).

## API
- `GET /api/health` – health check
- `POST /api/generate` – generate a password
- `POST /api/history` – save a generated password (requires `ENABLE_HISTORY=true`)
- `GET /api/history` – retrieve demo history (requires `ENABLE_HISTORY=true`)
- `DELETE /api/history` – clear demo history (requires `ENABLE_HISTORY=true`)

## Optional MySQL
Install a MySQL server and driver:
```bash
pip install pymysql
```
Set in `backend/.env`:
```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/password_generator
```
Create the database first. SQLite is used when `DATABASE_URL` is not set.

## GitHub deliverables
Suggested repository name: `Strong-Password-Generator`
Include screenshots of the UI, a short demo GIF, and a README section describing the API and security decisions.
