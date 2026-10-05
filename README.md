# Voltio backend

FastAPI API for electricity prices and forecasts. Python 3.14, Poetry.

## Local launch

Run commands from `backend/`:

```sh
poetry install
```

Copy `.env.example` to `app/.env`, enter your ENTSO-E key and frontend origins.
Origins use JSON array syntax, for example `["https://your-frontend.example"]`.
Do not commit the real key. `COUNTRY=PL` is the supported default; models and
holiday features currently use Polish market assumptions.

Prepare data and models, then start the API:

```sh
poetry run python -m app.services.forecast_refresh
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
```

Automatic updates are enabled by default (`FORECAST_REFRESH_ENABLED=true`). A daemon
thread starts preparation immediately after server startup and repeats it at
`FORECAST_REFRESH_SECONDS` intervals after each completed attempt. Failures are
logged and retried; the last published forecast is retained. Training only runs
when models are absent. To retrain, stop the web service and run:

```sh
poetry run python -m app.services.forecast_refresh --retrain
```

Do not run this command concurrently with the automatic refresh process.
For manual-only preparation, set `FORECAST_REFRESH_ENABLED=false` before starting
the web service. Otherwise, simply starting Uvicorn also prepares missing or stale data.
The first preparation fetches two years of historical data and trains four models;
it can take substantial time. API requests never initiate training or ENTSO-E calls.

## Render

Create a Blueprint from this repository using the root `render.yaml`.
Enter `ENTSOE_API_KEY` and `CORS_ORIGINS` when prompted. The blueprint selects a
**paid 1 CPU / 2 GB service and a 5 GB persistent disk**. Review the cost before
creating the service; actual memory requirements depend on the dataset.

Equivalent manual configuration:

| Setting | Value |
| --- | --- |
| Root Directory | `backend` |
| Python | `3.14.7` |
| Build | `pip install poetry==2.4.3 && poetry install --only main --no-interaction` |
| Start | `poetry run uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1` |
| Health Check Path | `/health` |
| Disk mount | `/var/data` |
| DATA_DIR | `/var/data` |
| FORECAST_REFRESH_ENABLED | `true` |

The port opens immediately. Until preparation completes, forecast endpoints and
`/ready` return 503. Check Render logs for refresh failures and `GET /ready` for
readiness. `/health` checks the HTTP server and is deliberately independent of
ENTSO-E availability. No training command belongs in Build or Pre-deploy: Render's
persistent disk is only available at runtime.

Use **one worker and one service instance** for this disk-backed design. Render
disks cannot be shared with a separate worker/cron service; moving training to
another service would require shared object storage or a database. The Free plan
has no persistent disk and is unsuitable for this configuration.

## API

- `/`, `/health`: basic server status.
- `/ready`: checks a fresh forecast covering the current Warsaw calendar day.
- `/forecast?period=24h|1w|1m`: saved forecast for 1, 7 or 30 calendar days,
  starting at midnight in `Europe/Warsaw`, with `updated_at` in UTC.
- `/api/dashboard/highlights`, `/api/dashboard/drivers`: today's values versus
  yesterday in the same timezone.
- `/docs`: interactive API documentation.

Saved forecasts must cover every requested 15-minute interval. Missing, corrupt,
expired or incomplete forecasts return 503; expiry defaults to 24 hours.
Existing JSON fields are retained and `updated_at` is added to `/forecast`.

## Tests

Run from `backend/` with a dummy key (no live ENTSO-E requests):

```sh
ENTSOE_API_KEY=test-api-key poetry run pytest -q
```

PowerShell: `$env:ENTSOE_API_KEY = 'test-api-key'; poetry run pytest -q`.

References: [Render Blueprints](https://render.com/docs/blueprint-spec),
[persistent disks](https://render.com/docs/disks),
[FastAPI deployment](https://render.com/docs/deploy-fastapi).
