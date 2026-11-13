# Local evidence API

Next.js route handlers in `prototype/app/api/` expose the Python stdlib service on the same localhost:3000 origin. No separate HTTP server or external database is required. `storage.py` imports source evidence into ignored local SQLite; `daily_index.py` indexes archived daily NASA records. `local_service.py` saves anonymous field submissions and immutable, source-linked reports.

Run `make backend` at the repository root, then start the existing frontend. See [DATA_INTEGRATION](../../docs/DATA_INTEGRATION.md) for IDs, metric definitions, API behavior and source gates.

A complete evidence report can still have incomplete crop planning. Never turn printed weather normals into crop thresholds, use future weather observations outside the archive, or invent alternatives/scores to fill the UI. Crop rules remain inactive until their source, applicability, metric, event and review definitions are supplied. The service has no regression training target.
