from __future__ import annotations

import argparse
import json
from pathlib import Path

from .queue import TelemetryBuffer


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect or enqueue events in a local edge telemetry buffer.")
    parser.add_argument("database", type=Path)
    subparsers = parser.add_subparsers(dest="command", required=True)
    enqueue = subparsers.add_parser("enqueue")
    enqueue.add_argument("payload", help="JSON object")
    subparsers.add_parser("summary")
    args = parser.parse_args()
    buffer = TelemetryBuffer(args.database)
    try:
        if args.command == "enqueue":
            print(json.dumps({"id": buffer.enqueue(json.loads(args.payload))}))
        else:
            print(json.dumps(buffer.summary(), sort_keys=True))
    finally:
        buffer.close()
