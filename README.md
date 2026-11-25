# AssetFlow — Asset Management System

**Internship task:** PY-EN-004 · Enterprise Asset Management  
**Stack:** Python, FastAPI, SQLAlchemy, MySQL 8, Bootstrap 5, JavaScript, ReportLab, OpenPyXL.

## Implemented modules
- Asset inventory and unique asset IDs, device details, purchase/warranty data, status and location
- Asset categories, departments and employee directory
- Assign assets to employees and record returns
- Schedule maintenance and mark maintenance complete
- Asset audits and asset disposal records
- Dashboard metrics and PDF / Excel inventory exports
- JWT authentication for REST API and interactive Swagger documentation

## Setup (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Create the MySQL database and user:
```sql
CREATE DATABASE asset_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'asset_user'@'localhost' IDENTIFIED BY 'change_this_password';
GRANT ALL PRIVILEGES ON asset_db.* TO 'asset_user'@'localhost';
FLUSH PRIVILEGES;
```
Copy `.env.example` to `.env`, then update `DATABASE_URL` and `SECRET_KEY`. Example:
```env
DATABASE_URL=mysql+pymysql://asset_user:change_this_password@localhost:3306/asset_db?charset=utf8mb4
SECRET_KEY=replace-with-a-long-random-secret
```
For a quick smoke test without MySQL, the project defaults to SQLite if no `DATABASE_URL` is supplied. The target configuration for the internship task is MySQL.

Run:
```powershell
uvicorn app.main:app --reload
```
Open `http://127.0.0.1:8000` for the dashboard, `http://127.0.0.1:8000/docs` for API docs, and `/health` for a health check.

## First-time API use
1. Call `POST /api/auth/register` with `{"username":"admin","email":"admin@example.com","password":"ChangeMe123"}`.
2. In Swagger, call `POST /api/auth/login` using the username and password form fields.
3. Click **Authorize** and provide the returned bearer token.
4. Use the authenticated endpoints to create departments, categories, employees, assets, assignments, maintenance records and audits.

## API route summary
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Obtain JWT |
| GET | `/api/dashboard` | Dashboard counts |
| GET / POST | `/api/assets` | List / create assets |
| GET / PUT / DELETE | `/api/assets/{id}` | Read / update / delete asset |
| GET / POST | `/api/categories` | Asset categories |
| GET / POST | `/api/departments` | Departments |
| GET / POST | `/api/employees` | Employees |
| GET / POST | `/api/assignments` | List / assign assets |
| POST | `/api/assignments/{id}/return` | Return asset |
| GET / POST | `/api/maintenance` | Maintenance records |
| PATCH | `/api/maintenance/{id}/complete` | Complete maintenance |
| GET / POST | `/api/audits` | Asset audits |
| POST | `/api/disposals` | Dispose an asset |
| GET | `/api/reports/summary` | Reporting metrics |
| GET | `/reports/assets.pdf` | Download PDF report |
| GET | `/reports/assets.xlsx` | Download Excel report |

## Important implementation notes
- JWT protects the REST API; registration and login are public. The HTML dashboard is a read-only overview and the asset/maintenance pages display records. Use Swagger `/docs` for authenticated data management.
- Tables are created automatically at startup for straightforward local setup. Alembic is included but migration scripts are not pre-generated.
- This is an internship/demo baseline, not production-certified software. Before production, add role-based access, CSRF protection for browser forms, pagination, comprehensive audit trails, database backups, stronger validation, and deployment hardening.
