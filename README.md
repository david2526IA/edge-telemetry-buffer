# Edge Telemetry Buffer

A small SQLite-backed durable queue for offline-first telemetry prototypes. It gives an edge application explicit `pending → inflight → delivered` state transitions and preserves failed events for retry.

It does not open a network connection or include credentials. A deployment can connect it to an approved sender while keeping buffering and delivery state testable locally.

## Example

```bash
pip install .
edge-buffer edge.db enqueue '{"asset_id":"PUMP-01","temperature":42.0}'
edge-buffer edge.db summary
```

Python applications can use `enqueue`, `claim`, `acknowledge` and `requeue`. Each claim increments an attempt count, and invalid state transitions are rejected.

## Scope

Reference software for prototypes and internal integration. A production deployment needs capacity limits, concurrency design, encryption, observability, authentication and recovery procedures appropriate to its environment.

## Development

```bash
pip install ".[dev]"
pytest -q
```

## License

MIT
