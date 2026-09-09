# Local Database

These instructions start PostgreSQL and Mailpit for local FastAPI development.

## Prerequisites

The commands below use Podman with `podman-compose` and the repository's
`compose.yml` files. Podman must use `netavark` for networking and a working OCI
runtime such as `crun`.

If Podman rejects short image names, create
`~/.config/containers/registries.conf` with trusted aliases:

```toml
[aliases]
"postgres" = "docker.io/library/postgres"
"adminer" = "docker.io/library/adminer"
"traefik" = "docker.io/library/traefik"
"axllent/mailpit" = "docker.io/axllent/mailpit"
```

If Homebrew's `nft` or `crun` is installed alongside Ubuntu's versions, make
sure Podman uses the working binaries. For example:

```bash
export PATH="/usr/sbin:/sbin:$PATH"
export CONTAINERS_CONF="$HOME/.config/containers/containers.conf"
```

The current Podman setup uses this runtime configuration in
`~/.config/containers/containers.conf`:

```toml
[engine]
runtime = "/home/linuxbrew/.linuxbrew/bin/crun"
```

## Start PostgreSQL and Mailpit

Run this from the project root:

```bash
uv run podman-compose \
  -f compose.yml \
  -f compose.override.yml \
  up -d db mailpit
```

The override file publishes these ports:

- PostgreSQL: `localhost:5432`
- Mailpit SMTP: `localhost:1025`
- Mailpit web interface: `http://localhost:8025`

Check the service status:

```bash
uv run podman-compose \
  -f compose.yml \
  -f compose.override.yml \
  ps
```

## Prepare the Database

From the `backend` directory, install dependencies and apply migrations:

```bash
cd backend
uv sync
uv run bash scripts/prestart.sh
```

This upgrades the database schema and creates the initial superuser from the
project `.env` file.

## Run the Application

Start FastAPI from the `backend` directory:

```bash
uv run fastapi dev app/main.py
```

In a separate terminal, start the frontend:

```bash
cd frontend
bun install
bun dev
```

Open the frontend at <http://localhost:5173>. The backend API is available at
<http://localhost:8000>, and its health check is at
<http://localhost:8000/api/v1/utils/health-check/>.

## Stop the Services

Stop FastAPI and Vite with `Ctrl+C` in their terminals. Then, from the project
root, stop the containers:

```bash
uv run podman-compose \
  -f compose.yml \
  -f compose.override.yml \
  down
```

This removes the containers and network but preserves the PostgreSQL volume.
Do not use `down -v` unless you intentionally want to delete the database data.

## Troubleshooting

If FastAPI returns an error for `/`, use the Vite URL at
<http://localhost:5173> while running the separate frontend workflow. FastAPI
serves the frontend from `backend/app/frontend` only after a frontend build:

```bash
cd frontend
bun run build
```

If a port is already in use, check running services:

```bash
podman ps
ss -ltnp | grep -E ':5432|:8000|:5173|:8025|:1025' || true
```
