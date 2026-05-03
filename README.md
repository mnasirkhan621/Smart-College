# Smart College Management System

This repository contains the Smart College Management System described in the project proposal PDF.

Part 1 is the foundation:

- Portable Django project setup
- Role-based users: Admin, Teacher, Student
- Login/logout flow
- Role-specific dashboards
- College setup models: departments, academic years, semesters, system settings
- Demo seed users
- SQLite local setup and optional PostgreSQL Docker setup

Part 2 adds the academic database:

- Student and faculty profiles
- Courses, subjects, classes, semesters, and academic years
- Student enrollments
- Teacher subject assignments
- Role dashboards backed by academic records

Part 3 adds attendance and communication:

- Teacher attendance sessions
- Student attendance records and percentages
- Admin low-attendance report
- Role-targeted notices

Part 4 adds exams and results:

- Exam terms and subject schedules
- Teacher marks entry
- Automatic result publishing
- Student result cards
- Promotion records

Part 5 adds fees, reports, and backup:

- Fee categories and structures
- Student invoices
- Payment receipts
- Pending dues report
- JSON backup command

## Local Setup

Install Python 3.11 or newer, then run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

Demo users:

```text
admin / Admin@12345
teacher / Teacher@12345
student / Student@12345
```

The seed command also creates a demo BSCS course, two first-semester subjects, one class group, one student profile, one faculty profile, enrollments, a teacher assignment, one attendance session, attendance records, grade scales, one exam schedule, marks, a published result, a promotion record, one fee invoice, a partial payment receipt, and demo notices.

## Backup

Create a JSON backup of application data:

```powershell
python manage.py backup_data
```

Backups are written to:

```text
backups/
```

## Docker Setup

Docker mode defaults to PostgreSQL and can run without editing configuration:

```powershell
docker compose up --build
```

Optional: copy `.env.example` to `.env` if you want to override credentials or debug settings.

```powershell
copy .env.example .env
docker compose up --build
```

Open:

```text
http://127.0.0.1:8000/
```

## Implementation Parts

See [SCMS_IMPLEMENTATION_PLAN.md](SCMS_IMPLEMENTATION_PLAN.md) for the complete 5-part roadmap.
