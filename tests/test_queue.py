from edge_telemetry_buffer.queue import TelemetryBuffer


def test_events_survive_claim_requeue_and_acknowledgement(tmp_path) -> None:
    buffer = TelemetryBuffer(tmp_path / "edge.db")
    event_id = buffer.enqueue({"asset_id": "PUMP-01", "temperature": 42.0})
    claimed = buffer.claim()
    assert claimed == [{"id": event_id, "payload": {"asset_id": "PUMP-01", "temperature": 42.0}, "attempt": 1}]
    buffer.requeue(event_id, "network unavailable")
    claimed_again = buffer.claim()
    assert claimed_again[0]["attempt"] == 2
    buffer.acknowledge(event_id)
    assert buffer.summary() == {"delivered": 1}
    buffer.close()


def test_state_transitions_are_enforced(tmp_path) -> None:
    buffer = TelemetryBuffer(tmp_path / "edge.db")
    event_id = buffer.enqueue({"event": "ok"})
    try:
        buffer.acknowledge(event_id)
    except ValueError as error:
        assert "inflight" in str(error)
    else:
        raise AssertionError("expected transition error")
    buffer.close()
