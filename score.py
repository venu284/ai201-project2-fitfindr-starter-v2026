#!/usr/bin/env python3
"""
Score one capstone trial against the criteria in criteria.md. Capstone (unit 9).

    python score.py 1          scores trial 1 (labels c1-burst-t1, c2-paced-t1, ...)

This script does not define the criteria; it applies the thresholds written in
criteria.md to the driver's caller-side rows (results/drive_<label>.json) and
the service's own records (logs/requests.jsonl, joined by run_label).
"""

import json
import sys
from pathlib import Path

import runlog

ROOT = Path(__file__).resolve().parent


def caller_rows(label: str) -> list[dict]:
    path = ROOT / "results" / f"drive_{label}.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))["rows"]


def log_records(label: str) -> list[dict]:
    return [r for r in runlog.read_records() if r.get("run_label") == label]


def verdict(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def c1(n: int) -> tuple[bool, str]:
    label = f"c1-burst-t{n}"
    rows, recs = caller_rows(label), log_records(label)
    ids = {r["request_id"] for r in recs}
    logged = sum(1 for row in rows if row["request_id"] in ids)
    return logged == 10 and len(rows) == 10, f"requests with a log record: {logged} of {len(rows)}"


def c2(n: int) -> tuple[bool, str]:
    label = f"c2-paced-t{n}"
    recs = log_records(label)
    times = [r["total_ms"] for r in recs]
    within = sum(1 for t in times if t is not None and t <= 2500)
    return (len(recs) == 10 and within >= 9,
            f"{within} of {len(recs)} records with total_ms <= 2500; total_ms = {times}")


def c3(n: int) -> tuple[bool, str]:
    label = f"c2-paced-t{n}"
    recs = log_records(label)
    good = [r for r in recs
            if r["outcome"] == "fit_card"
            and r["model_calls"] == 2
            and r["prompt_tokens"] + r["output_tokens"] <= 1300]
    detail = [(r["outcome"], r["model_calls"], r["prompt_tokens"] + r["output_tokens"]) for r in recs]
    return (len(recs) == 10 and len(good) == 10,
            f"{len(good)} of {len(recs)} records are fit_card with 2 calls and <= 1300 tokens; "
            f"(outcome, calls, tokens) = {detail}")


def c4(n: int) -> tuple[bool, str]:
    label = f"c1-burst-t{n}"
    rows = caller_rows(label)
    by_id = {r["request_id"]: r for r in log_records(label)}
    good, bad = 0, []
    for i, row in enumerate(rows, 1):
        rec = by_id.get(row["request_id"]) or {}
        ok = (
            row["status"] == 200
            and row["client_error"] is None
            and row["client_ms"] <= 65000
            and (rec.get("outcome") == "fit_card"
                 or (rec.get("outcome") == "model_error" and rec.get("error")))
        )
        if ok:
            good += 1
        else:
            bad.append(f"#{i} status={row['status']} client_ms={row['client_ms']} "
                       f"error={row['client_error'] or row['outcome']!r}")
    return (len(rows) == 10 and good == 10,
            f"{good} of {len(rows)} returned 200 with fit_card or model_error within 65 s"
            + (f"; failing: {bad}" if bad else ""))


def c5(n: int) -> tuple[bool, str]:
    bad = log_records(f"c5-bad-t{n}")
    none = log_records(f"c5-nomatch-t{n}")
    bad_ok = sum(1 for r in bad if r["status"] == 400 and r["outcome"] == "bad_request")
    none_ok = sum(1 for r in none if r["outcome"] == "no_results")
    calls = sum(r["model_calls"] for r in bad + none)
    ok = len(bad) == 4 and bad_ok == 4 and len(none) == 2 and none_ok == 2 and calls == 0
    return ok, (f"{bad_ok} of {len(bad)} bad bodies got 400 bad_request; "
                f"{none_ok} of {len(none)} impossible queries got no_results; "
                f"model calls across all 6: {calls}")


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print("usage: python score.py <trial number>")
        return 2
    n = int(sys.argv[1])
    print(f"Trial {n}")
    for name, fn in (("C1", c1), ("C2", c2), ("C3", c3), ("C4", c4), ("C5", c5)):
        ok, detail = fn(n)
        print(f"  {name} {verdict(ok)}  {detail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
