# FinGuard competition deployment guide

This is a deployment checklist for a competition demo, not a security certification.

## Recommended architecture

- Frontend: Vercel (Next.js).
- Backend: a container host such as Render or Railway.
- PostgreSQL: managed PostgreSQL with TLS and private networking when available.
- Redis: managed Redis for Celery.
- LLM: an Ollama instance reachable by the backend, or a supported hosted provider implemented and reviewed in the app. The current provider uses Ollama at OLLAMA_BASE_URL; localhost inside a cloud container means that container itself, not your laptop.

Keep the database and Redis private. Expose only the HTTPS frontend and the API. Use synthetic documents and demo accounts.

## Before deploying

1. Review and merge the security pull request only after CI passes and you test locally.
2. Create a separate production secret set in the hosting provider's secret manager. Never upload .env or paste credentials into issues/chat.
3. Generate SECRET_KEY with `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
4. Set APP_ENV=production, DEBUG=false, SECRET_KEY, DATABASE_URL, DATABASE_URL_SYNC, REDIS_URL, CELERY_BROKER_URL, OLLAMA_BASE_URL, and exact CORS_ORIGINS.
5. Use a unique database password and TLS-enabled database URLs. Do not expose PostgreSQL or Redis to the public internet.
6. Set CORS_ORIGINS to the exact frontend origin, e.g. https://your-project.vercel.app (no trailing slash). Do not use a wildcard.
7. Ensure a Celery worker is running using the same backend image and configuration, with command: `celery -A app.workers.celery_app worker --loglevel=INFO`. Verify the actual Celery app module name in the repository before using this command.
8. Use persistent, access-controlled storage for uploads. The current local upload path is ephemeral on many container hosts; do not assume files survive redeploys.
9. Verify the production health endpoint at `https://YOUR_API_HOST/api/health`, then test registration, login, upload, document processing, report access, and cross-account access denial.
10. Configure backups, retention/deletion, logs without secrets/document contents, and an incident contact.

## Local smoke test

From the repository root, create a local `.env` from `.env.example` and replace every placeholder. Ensure POSTGRES_PASSWORD matches the password in both database URLs (URL-encode special characters). Then:

```bash
docker compose config
docker compose up -d postgres
```

Start the API in the backend virtual environment and run the frontend separately. Do not expose port 5555 to your LAN. If the PostgreSQL volume already existed, rotating POSTGRES_PASSWORD in .env alone does not change the database role password inside that volume.

## Production blockers to address before accepting real users

- Move access/refresh tokens out of localStorage into a reviewed session design; HttpOnly/Secure/SameSite cookies require CSRF protections where applicable.
- Add shared, distributed rate limiting for login/register/refresh and sensitive endpoints.
- Implement server-side refresh-token rotation/revocation and invalidate sessions on logout/password changes.
- Add integration tests for tenant/document ownership, file parser resource limits, malformed files, and prompt injection.
- Add upload malware scanning or process documents in a tightly isolated worker with CPU, memory, time, and network limits.
- Confirm the dependency audit is clean and review/upgrade any vulnerable packages.
- Add database migrations and backups/restore drills; confirm storage encryption and access policy.

Do not claim the app is 100% secure. For the competition, explicitly label it a prototype and use synthetic financial data only.
