# Okten Next JS Project (base setup)

Base scaffold with:
- Django + DRF backend
- PostgreSQL + Redis
- Docker Compose
- Nginx reverse proxy

## Quick start

1. Copy env:
   - `backend/.env.example` -> `backend/.env`
2. Run:
   - `cd infra`
   - `docker compose up --build`
3. Check:
   - `http://localhost/api/health/`
   - `http://localhost/admin/`

## Notes

- This is intentionally minimal foundation only.
- Domain models, business logic, and frontend app are left for next steps.
