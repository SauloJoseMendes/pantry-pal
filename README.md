# Pantry Pal

Track what's in your pantry and find recipes you can cook with it.

## Project status

Early development — database design phase.

## Tech stack

- **FastAPI** — web framework
- **PostgreSQL** — database (via psycopg)
- **Pydantic** — data validation
- **pytest** — testing
- **ruff** — linting & formatting
- **mypy** — type checking

## Database setup

Migrations live in `db/migrations/` and are applied in filename order.
The editable ERD source is at `docs/erd/pantry-pal-diagram.json`.

To create the schema on a fresh database:

```bash
psql -U &lt;user&gt; -d &lt;db_name&gt; -f db/migrations/001_initial_schema.sql