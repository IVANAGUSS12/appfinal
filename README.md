# Autorizaciones (Login → Menú → Sector)
- **Login principal** (`/login.html`)
- **Menú por especialidad** (`/menu.html`)
- **Sector** (`/sector.html?code=...`) con mover pacientes entre sectores
- **Calendario** (`/calendar.html` + `calendar_day.html`)
- **Estadísticas** (`/stats.html`)
- **QR** (`/qr.html`) usando listas desde DB (Médicos/Sectores/Coberturas)
- **Importador** (`/admin/importar.html`) acepta CSV o **XLS-HTML** y deduplica

API:
- `/api/ref/lists`, `/api/ref/import/csv`, `/api/ref/import/xls-html`
- `/api/patients` (GET, POST), `/api/patients/{id}` (PATCH)
- `/api/calendar-month`, `/api/calendar-day`, `/api/stats`
