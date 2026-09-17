# Pantry Pal

Track what's in your pantry and find recipes you can cook with it.

## Project status

Early development — database design phase.

## Tech stack

- MySQL (or whatever you're targeting)
- ERD maintained with [your diagram tool]

## Database setup

Migrations live in `db/migrations/` and are applied in filename order.
The editable ERD source is at `docs/erd/pantry-pal-diagram.json`.

To create the schema on a fresh database:

```bash
mysql -u &lt;user&gt; -p &lt;db_name&gt; &lt; db/migrations/001_initial_schema.sql
```
