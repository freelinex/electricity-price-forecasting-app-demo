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
The first preparation fetches `HISTORY_DAYS` days of historical data (730 locally,
90 in the Render Free configuration) and trains four models;
it can take substantial time. API requests never initiate training or ENTSO-E calls.

## Render

For a free demo, select New > Web Service, connect your repository and choose
the **Free** instance type. Alternatively, the root `render.yaml` now defines
`plan: free` and has no persistent disk. Enter `ENTSOE_API_KEY` and `CORS_ORIGINS`.

Equivalent manual configuration:

| Setting | Value |
| --- | --- |
| Root Directory | `backend` |
| Python | `3.14.7` |
| Build | `pip install poetry==2.4.3 && poetry install --only main --no-interaction` |
| Start | `poetry run uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1` |
| Health Check Path | `/health` |
| Instance Type | `Free` |
| DATA_DIR | `/tmp/voltio-data` |
| HISTORY_DAYS | `90` |
| FORECAST_REFRESH_ENABLED | `true` |
| OMP_NUM_THREADS | `1` |

The port opens immediately. Until preparation completes, forecast endpoints and
`/ready` return 503. Check Render logs for refresh failures and `GET /ready` for
readiness. `/health` checks the HTTP server and is deliberately independent of
ENTSO-E availability. Preparation runs in the background at runtime.

Use **one worker and one service instance** for this file-based design. Free
instances spin down after 15 minutes without inbound traffic, and local files
are lost on spin-down, restart or redeploy. Each fresh start therefore downloads
data and retrains models; forecast endpoints return 503 until that completes.
The Free instance has 512 MB RAM and limited CPU. The 90-day history and
single-threaded models reduce resource use, but training has not been measured
on Render Free; an out-of-memory failure is still possible. A shorter history
also changes model quality and omits annual seasonality.

For faster recovery on Free, the next step is storing prepared data and models
externally, then downloading them on startup. A persistent disk requires a paid
service; the current free configuration does not provision one.

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
