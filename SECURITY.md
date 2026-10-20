# Security baseline

## Local development

1. Copy `.env.example` to `.env`.
2. Replace all `REPLACE_...` placeholders. Generate `SECRET_KEY` with:
   `python -c "import secrets; print(secrets.token_urlsafe(48))"`
3. Use the same unique database password in `POSTGRES_PASSWORD`, `DATABASE_URL`, and `DATABASE_URL_SYNC`. URL-encode special characters in the URL password.
4. Start Compose from the repository root so it reads the root `.env` file.
5. The database port is bound to `127.0.0.1`; it should not be reachable directly from other machines.

The local development configuration is not suitable for public deployment.

## Before production

- Set `APP_ENV=production`, `DEBUG=false`, and unique production-only credentials.
- Set a random `SECRET_KEY` of at least 32 characters; never reuse development secrets.
- Use a managed/isolated database and restrict network access to the application only.
- Configure exact trusted CORS origins and HTTPS.
- Add login/register/refresh rate limits and server-side refresh-token revocation.
- Replace browser `localStorage` token storage with a reviewed secure session design (typically HttpOnly, Secure, SameSite cookies plus CSRF protections where applicable).
- Add security tests for authorization/ownership, upload parsing/resource limits, and prompt-injection handling.
- Scan the complete Git history for accidentally committed secrets. If a real secret was ever committed, rotate it; deleting the file is not sufficient.

## If the database volume already exists

Changing `POSTGRES_PASSWORD` in Compose does not automatically change the password inside an already-initialized PostgreSQL data volume. Change the database role password inside PostgreSQL as a separate migration step before relying on the new value.
