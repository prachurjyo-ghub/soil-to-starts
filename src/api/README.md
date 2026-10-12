# Local API boundary

The API is planned, not implemented. Its first useful response should be a rotation comparison for a selected location, field context, and priorities. Each result should carry values, units, source IDs, dates, assumptions, limitations, and a `data_mode` such as `fixture` or `cache`. Invalid or missing inputs should return an explicit error or unavailable result. The proposed response fields and flow are in [`docs/ARCHITECTURE.md`](../../docs/ARCHITECTURE.md).

Keep NASA downloads in `src/acquire/`; serving a demo should read local processed data. A planting-window endpoint can be added after the timing method is validated and connected to the rotation decision.
