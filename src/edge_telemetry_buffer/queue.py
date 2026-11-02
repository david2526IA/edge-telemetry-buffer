"""A small SQLite-backed queue with explicit delivery state transitions."""

from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any


class TelemetryBuffer:
    def __init__(self, database: Path) -> None:
        self.connection = sqlite3.connect(database)
        self.connection.execute("""create table if not exists events (
            id text primary key, payload text not null, state text not null,
            attempts integer not null default 0, last_error text
        )""")
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def enqueue(self, payload: dict[str, Any]) -> str:
        """Persist a JSON event before any external delivery attempt."""
        event_id = str(uuid.uuid4())
        self.connection.execute("insert into events (id, payload, state) values (?, ?, 'pending')", (event_id, json.dumps(payload, sort_keys=True)))
        self.connection.commit()
        return event_id

    def claim(self, limit: int = 10) -> list[dict[str, Any]]:
        """Atomically move pending events to inflight and return them."""
        if limit < 1:
            raise ValueError("limit must be at least 1")
        with self.connection:
            rows = self.connection.execute("select id, payload, attempts from events where state = 'pending' order by rowid limit ?", (limit,)).fetchall()
            ids = [row[0] for row in rows]
            if ids:
                self.connection.executemany("update events set state = 'inflight', attempts = attempts + 1 where id = ?", [(event_id,) for event_id in ids])
        return [{"id": event_id, "payload": json.loads(payload), "attempt": attempts + 1} for event_id, payload, attempts in rows]

    def acknowledge(self, event_id: str) -> None:
        with self.connection:
            updated = self.connection.execute("update events set state = 'delivered', last_error = null where id = ? and state = 'inflight'", (event_id,)).rowcount
        if updated != 1:
            raise ValueError("only inflight events can be acknowledged")

    def requeue(self, event_id: str, error: str) -> None:
        with self.connection:
            updated = self.connection.execute("update events set state = 'pending', last_error = ? where id = ? and state = 'inflight'", (error, event_id)).rowcount
        if updated != 1:
            raise ValueError("only inflight events can be requeued")

    def summary(self) -> dict[str, int]:
        rows = self.connection.execute("select state, count(*) from events group by state").fetchall()
        return {state: count for state, count in rows}
