#!/usr/bin/env python3
"""Rebuild one or all Velt Chroma collections from PostgreSQL."""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.search_engine import SemanticSearchEngine
from app.models.database import Store
from app.services.index_rebuild import rebuild_store_index


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--store-id", action="append", dest="store_ids")
    target.add_argument("--all-stores", action="store_true")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--confirm-destructive-rebuild", action="store_true")
    args = parser.parse_args()

    if not args.confirm_destructive_rebuild:
        parser.error("--confirm-destructive-rebuild is required because existing collections are replaced")
    if args.batch_size < 1 or args.batch_size > 5000:
        parser.error("--batch-size must be between 1 and 5000")

    started_at = datetime.now(UTC)
    db = SessionLocal()
    engine = SemanticSearchEngine(db_path=settings.CHROMA_DB_PATH)
    results = []
    exit_code = 0
    error = None
    try:
        store_ids = args.store_ids
        if args.all_stores:
            store_ids = [row[0] for row in db.query(Store.id).order_by(Store.id).all()]
        for store_id in store_ids or []:
            started = time.perf_counter()
            result = rebuild_store_index(db, engine, store_id, args.batch_size)
            results.append({**asdict(result), "duration_ms": round((time.perf_counter() - started) * 1000, 2)})
    except Exception as exc:
        exit_code = 1
        error = str(exc)[:500]
        print(f"Index rebuild failed: {error}", file=sys.stderr)
    finally:
        db.close()

    report = {
        "schema_version": 1,
        "started_at": started_at.isoformat(),
        "finished_at": datetime.now(UTC).isoformat(),
        "passed": exit_code == 0,
        "error": error,
        "stores": results,
    }
    output = args.output or Path("artifacts") / f"chroma-rebuild-{started_at:%Y%m%dT%H%M%SZ}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Evidence report: {output}")
    print(f"Rebuilt stores: {len(results)}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
