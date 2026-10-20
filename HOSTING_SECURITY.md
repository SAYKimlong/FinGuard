# FinGuard competition deployment (single VPS)

This is a practical prototype deployment plan, not a security certification. Use synthetic financial documents and demo accounts only.

## Architecture

A single Ubuntu VPS runs Docker Compose: Caddy (public HTTPS), Next.js, FastAPI, Celery worker, PostgreSQL/pgvector, Redis, and Ollama. PostgreSQL, Redis, Ollama, API, and frontend are on a private Docker network; only Caddy publishes ports 80 and 443. DuckDNS supplies a free hostname.

## VPS sizing and cost

- Start with 4 vCPU / 8 GB RAM / 80+ GB SSD for a low-cost CPU-only demo. If the budget allows, 8 vCPU / 16 GB RAM will be noticeably more comfortable for Ollama plus the worker/database.
- Expect CPU inference to be slower than GPU inference; test the model before judging day. Disk space must cover Docker images, model weights, PostgreSQL, and uploaded files.
- VPS prices and availability vary by region and provider; compare current prices and data-center locations before purchasing. Back up the database and uploads to storage outside the VPS.

## 1. Prepare a VPS

Provision Ubuntu 24.04 LTS. Add an SSH key during provisioning. In the provider firewall, allow inbound TCP 22 only from your IP if possible, plus TCP 80 and 443 from anywhere. Do not open ports 3000, 5432, 5555, 6379, 8000, or 11434.

Connect as the provider's default user, then install Docker Engine and Compose plugin using Docker's official Ubuntu instructions:
https://docs.docker.com/engine/install/ubuntu/

Update the OS and install small utilities:
```bash
sudo apt update && sudo apt -y upgrade
sudo apt -y install git openssl
```

Install Docker from its official repository, then verify:
```bash
docker --version
docker compose version
```

## 2. Set up free DNS

1. Visit https://www.duckdns.org and sign in.
2. Create a unique subdomain, e.g. `finguard-yourname.duckdns.org`, and copy the DuckDNS token privately.
3. Create the `.env` file as described below, using the exact same subdomain for `DUCKDNS_SUBDOMAIN` (without `.duckdns.org`) and `DOMAIN` (with it).
4. Ensure the VPS provider firewall permits inbound ports 80 and 443. DNS propagation can take a little time. Caddy will request the HTTPS certificate once DNS points to the VPS.

## 3. Clone and configure

```bash
git clone https://github.com/SAYKimlong/FinGuard.git
cd FinGuard
git checkout main
cp .env.production.example .env
chmod 600 .env
```

Edit `.env`:
- Set `DUCKDNS_SUBDOMAIN`, `DOMAIN`, and `DUCKDNS_TOKEN`.
- Generate `SECRET_KEY` on the VPS with `python3 -c 'import secrets; print(secrets.token_urlsafe(48))'`.
- Generate separate passwords with `openssl rand -hex 32`; use one for PostgreSQL and a different one for Redis.
- Replace the placeholder password in both database URLs with the exact `POSTGRES_PASSWORD` value. Replace the Redis password in both Redis URLs with the exact `REDIS_PASSWORD` value.
- Set `CORS_ORIGINS=https://YOUR_SUBDOMAIN.duckdns.org` (exact origin, no trailing slash).
- Leave `APP_ENV=production`, `DEBUG=false`, `OLLAMA_BASE_URL=http://ollama:11434`, `UPLOAD_DIR=/app/storage/uploads`.
- For a small CPU-only VPS, start with `LLM_MODEL=llama3.2:3b`; it uses fewer resources than the default 8B model, though answer quality may differ. Keep `EMBEDDING_MODEL=nomic-embed-text`.

Never commit `.env`, share it in screenshots, or paste secrets into chat. `.env.production.example` is only a template; the real `.env` must be populated.

## 4. Validate configuration and build

Run:
```bash
docker compose --env-file .env -f docker-compose.prod.yml config --quiet
docker compose --env-file .env -f docker-compose.prod.yml build
```

If Compose reports a missing variable or invalid YAML, stop and fix it before starting services.

## 5. Start services and pull AI models

```bash
docker compose --env-file .env -f docker-compose.prod.yml up -d
docker compose --env-file .env -f docker-compose.prod.yml ps
docker compose --env-file .env -f docker-compose.prod.yml logs -f ollama-models
```

The first start downloads the model and embedding weights; this can take time and significant disk/network bandwidth. Wait for the model pull to finish, then check:
```bash
docker compose --env-file .env -f docker-compose.prod.yml logs --tail=100 api worker caddy
curl -fsS https://YOUR_SUBDOMAIN.duckdns.org/api/health
```

Expected health response is JSON containing `"status":"healthy"`. Confirm HTTPS certificate issuance and verify from a separate network that only ports 80/443 (and your restricted SSH) are reachable.

## 6. Test the full demo

- Register two test users with non-reused passwords.
- Log in as user A, upload a synthetic PDF/DOCX, and verify it completes processing.
- Test clause Q&A, report generation, and the financial calculations.
- Log in as user B and verify attempts to access user A's document IDs return not found/denied.
- Test an unsupported file extension, a renamed non-PDF file, and an oversized upload.
- Restart the stack and verify model files, database, Redis, and uploads persist.

Do not use real bank statements, identity documents, or customer financial data for the public demo.

## 7. Operations

View logs:
```bash
docker compose --env-file .env -f docker-compose.prod.yml logs -f --tail=200
```

Update after reviewing changes:
```bash
git pull
docker compose --env-file .env -f docker-compose.prod.yml build
docker compose --env-file .env -f docker-compose.prod.yml up -d
```

Back up PostgreSQL and the `uploaded_documents` volume to encrypted off-server storage; test restoration. Protect the DuckDNS token and .env. Keep Ubuntu and images patched. Use a provider firewall and avoid exposing internal ports.

## Known limitations / changes to finish before real users

- The frontend still stores access and refresh tokens in localStorage; XSS could steal them. A reviewed HttpOnly/Secure/SameSite session design and CSRF controls are recommended.
- Add shared rate limiting for login, registration, refresh, upload, and LLM endpoints, and implement server-side refresh-token rotation/revocation.
- Add a committed frontend lockfile and use `npm ci`; run frontend vulnerability auditing and fix high/critical findings before public launch.
- Review Python dependency audit output; do not suppress vulnerable packages without assessment.
- Uploaded files are on a Docker volume on one host; arrange encrypted off-host backups and consider isolated parser processing/malware scanning.
- Test the compose file, model pull, frontend build, database migration/schema creation, and all main flows on the actual VPS before announcing the URL.
- The app's current startup path does not visibly run Alembic migrations or create all ORM tables automatically. Verify database schema initialization and add a controlled migration step before relying on a fresh database.
- Do not claim FinGuard is 100% secure; this is a competition prototype with remaining risks.
