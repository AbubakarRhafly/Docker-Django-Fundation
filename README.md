# Simple LMS - Django + PostgreSQL with Docker

## Overview

Project ini merupakan setup environment development untuk aplikasi **Simple LMS** menggunakan **Django** dan **PostgreSQL** dengan **Docker Compose**.

## Learning Objectives

- Memahami containerization dengan Docker
- Membuat `Dockerfile` dan `docker-compose.yml`
- Setup project Django
- Menghubungkan Django dengan PostgreSQL

## Project Structure

```text
Progress01-Docker_&_Django_Foundation/
├── config/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── README.md
└── requirements.txt
```
## Services
* web : Django application
* db : PostgreSQL database

## Environment Variables
Buat file `.env` dari `.env.example`
Contoh isi:
```env
SECRET_KEY=django-insecure-change-this
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=simple_lms
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=db
DB_PORT=5432
```

## Run Project
```Bash
docker compose build
docker compose up -d
docker compose exec web python manage.py migrate
```
Buka di browser:
```
http://localhost:8000
```

## Database Configuration
Project ini menggunakan PostgreSQL yang dikonfigurasi di settings.py melalui environment variables.

## Result
Project berhasil dijalankan dengan hasil:
* Docker Compose running
* Django accessible di localhost:8000
* PostgreSQL connection working
* Migration berhasil dijalankan

## Screenshots
### Django Welcome Page
<img width="1917" height="1031" alt="Screenshot 2026-04-09 080659" src="https://github.com/user-attachments/assets/2efedc0b-ba14-4e31-9789-8cb51fc52418" />

### Docker Compose Status & Migration Result
<img width="1775" height="848" alt="Screenshot 2026-04-09 082116" src="https://github.com/user-attachments/assets/c2b6c080-1c90-4712-8f02-e5aa40095632" />

## Conclusion
Project Simple LMS berhasil dibuat menggunakan Django, PostgreSQL, dan Docker. Aplikasi dapat berjalan dengan baik di localhost:8000 dan database berhasil terhubung.
