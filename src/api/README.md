# Local API boundary

The API is planned, not implemented. Its first useful response should be a rotation comparison for a selected location, field context, and priorities. Each result should carry values, units, source IDs, dates, assumptions, limitations, and a `data_mode` such as `verified_fixture` or `cache`. Invalid or missing inputs should return an explicit error or unavailable result. The proposed response fields and flow are in [`docs/ARCHITECTURE.md`](../../docs/ARCHITECTURE.md).

Keep NASA downloads in `src/acquire/`; serving a demo should read local processed data. A planting-window endpoint can be added after the timing method is validated and connected to the rotation decision.

Follow [API_CONTRACT](../../docs/API_CONTRACT.md) for separate bundle/plan statuses, assessed baseline, distinct alternatives, shared quick checks and stable source/version receipts. No endpoints are implemented by this planning update.
