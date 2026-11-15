#!/usr/bin/env python3
"""
Replay a fixed set of queries against a running FitFindr service. Capstone (unit 9).

Start the service first (see RUNNING.md), then in a second terminal:

    python drive.py --set matching --repeat 2 --label cost-check
    python drive.py --set mixed --label trial1
    python drive.py --set matching --parallel 3 --label overlap

Every request carries an X-Run-Label header, so its line in logs/requests.jsonl
can be found later. The driver records what the *caller* saw (status, time,
connection errors), then joins that to the service's own log by request id.
A request the caller sent that has no log line is reported, because a missing
record is exactly the kind of failure a log should not hide.

The report goes to results/drive_<label>.md: one row per request, a summary,
and the matching log records pasted as JSON.
"""

import argparse
import json
import statistics
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import runlog

ROOT = Path(__file__).resolve().parent

# Five matching queries, chosen so each selects a different listing
# (lst_002, lst_007, lst_013, lst_039, lst_003) rather than the one listing
# every Unit 4 test selected.
MATCHING = [
    "vintage graphic tee under $30",
    "denim jacket under $60",
    "floral dress under $35",
    "leather bag",
    "flannel shirt under $25",
]
NO_MATCH = [
    "designer ballgown size XXS under $5",
    "wool sweater under $40",
]
# Bodies, not queries: each should be refused with a 400.
BAD = [
    {},
    {"query": ""},
    {"query": "   "},
    {"query": 42},
]

SETS = {
    "matching": [{"query": q} for q in MATCHING],
    "no_match": [{"query": q} for q in NO_MATCH],
    "bad": BAD,
}
SETS["mixed"] = SETS["matching"] + SETS["no_match"] + SETS["bad"]


def send(url: str, body: dict, label: str, timeout: float) -> dict:
    """POST one body to /ask and record what the caller saw."""
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{url}/ask",
        data=data,
        headers={"Content-Type": "application/json", "X-Run-Label": label},
        method="POST",
    )
    row = {"body": body, "status": None, "client_ms": None, "request_id": None,
           "outcome": None, "client_error": None}
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            row["status"] = resp.status
            row["request_id"] = resp.headers.get("X-Request-Id")
            payload = json.loads(resp.read() or b"{}")
            row["outcome"] = "fit_card" if payload.get("fit_card") else (payload.get("error") or "")[:60]
    except urllib.error.HTTPError as exc:
        row["status"] = exc.code
        row["request_id"] = exc.headers.get("X-Request-Id")
        try:
            row["outcome"] = (json.loads(exc.read() or b"{}").get("error") or "")[:60]
        except json.JSONDecodeError:
            row["outcome"] = "non-JSON error body"
    except Exception as exc:  # noqa: BLE001 — timeouts, resets, refused connections
        row["client_error"] = f"{type(exc).__name__}: {exc}"[:120]
    row["client_ms"] = round((time.perf_counter() - start) * 1000, 1)
    return row


def pct(values: list[float], p: float) -> float | None:
    """Nearest-rank percentile. None for an empty list."""
    if not values:
        return None
    ordered = sorted(values)
    rank = max(1, round(p / 100 * len(ordered) + 0.4999))
    return ordered[min(rank, len(ordered)) - 1]


def summarise(rows: list[dict], records: list[dict]) -> list[str]:
    by_id = {r["request_id"]: r for r in records}
    statuses: dict[str, int] = {}
    for row in rows:
        key = str(row["status"]) if row["status"] else "no response"
        statuses[key] = statuses.get(key, 0) + 1

    logged = [row for row in rows if row["request_id"] in by_id]
    agent_runs = [by_id[row["request_id"]] for row in logged
                  if by_id[row["request_id"]]["status"] == 200]
    fit_runs = [r for r in agent_runs if r["outcome"] == "fit_card"]
    client_ms = [row["client_ms"] for row in rows if row["status"] == 200]

    lines = [
        f"- requests sent: {len(rows)}",
        f"- status counts: " + ", ".join(f"{k}: {v}" for k, v in sorted(statuses.items())),
        f"- requests with a log record: {len(logged)} of {len(rows)}",
    ]
    if client_ms:
        lines.append(
            f"- caller-observed latency of 200s (ms): p50 {pct(client_ms, 50)}, "
            f"p90 {pct(client_ms, 90)}, max {max(client_ms)}"
        )
    if agent_runs:
        waits = [r["queue_wait_ms"] or 0 for r in agent_runs]
        lines.append(f"- queue wait (ms): mean {round(statistics.mean(waits), 1)}, max {max(waits)}")
    if fit_runs:
        tokens = [r["prompt_tokens"] + r["output_tokens"] for r in fit_runs]
        calls = [r["model_calls"] for r in fit_runs]
        lines.append(
            f"- fit-card runs: {len(fit_runs)}; tokens per run mean "
            f"{round(statistics.mean(tokens), 1)} (min {min(tokens)}, max {max(tokens)}); "
            f"model calls per run mean {round(statistics.mean(calls), 2)}; "
            f"cache hits {sum(r['cache_hits'] for r in fit_runs)}"
        )
        stages: dict[str, list[float]] = {}
        for r in fit_runs:
            for stage, ms in (r.get("stage_ms") or {}).items():
                stages.setdefault(stage, []).append(ms)
        lines.append("- mean stage time over fit-card runs (ms): " + ", ".join(
            f"{s} {round(statistics.mean(v), 1)}" for s, v in stages.items()))
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--set", choices=sorted(SETS), default="mixed")
    parser.add_argument("--repeat", type=int, default=1, help="passes through the set")
    parser.add_argument("--parallel", type=int, default=1, help="requests in flight at once")
    parser.add_argument("--timeout", type=float, default=300.0, help="caller timeout, seconds")
    parser.add_argument("--label", default=datetime.now().strftime("run_%Y-%m-%d_%H%M%S"))
    parser.add_argument("--log", type=Path, default=runlog.LOG_PATH,
                        help="the service's log file, to join against")
    args = parser.parse_args()

    bodies = SETS[args.set] * args.repeat
    print(f"Sending {len(bodies)} requests ({args.set} x{args.repeat}, "
          f"{args.parallel} at a time) to {args.url} as '{args.label}'")

    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        futures = [pool.submit(send, args.url, b, args.label, args.timeout) for b in bodies]
        rows = []
        for i, fut in enumerate(futures, 1):
            row = fut.result()
            rows.append(row)
            print(f"  [{i}/{len(bodies)}] {row['status'] or row['client_error']} "
                  f"{row['client_ms']}ms  {json.dumps(row['body'])[:50]}", flush=True)

    records = [r for r in runlog.read_records(args.log) if r.get("run_label") == args.label]
    summary = summarise(rows, records)

    out = ROOT / "results" / f"drive_{args.label}.md"
    lines = [
        f"# Drive run `{args.label}`",
        "",
        f"`python drive.py --set {args.set} --repeat {args.repeat} --parallel {args.parallel} "
        f"--label {args.label}` against {args.url}, finished {runlog.now_iso()}.",
        "",
        "## Summary",
        "",
        *summary,
        "",
        "## What the caller saw",
        "",
        "| # | body | status | caller ms | request_id | outcome / error |",
        "|---|---|---|---|---|---|",
    ]
    for i, row in enumerate(rows, 1):
        detail = row["client_error"] or row["outcome"] or ""
        lines.append(f"| {i} | `{json.dumps(row['body'])}` | {row['status'] or '-'} | "
                     f"{row['client_ms']} | {row['request_id'] or '-'} | {detail.replace('|', '/')} |")
    lines += ["", "## Log records for this label (logs/requests.jsonl)", "", "```json"]
    lines += [json.dumps(r, ensure_ascii=False) for r in records]
    lines += ["```", ""]
    out.write_text("\n".join(lines), encoding="utf-8")

    print("\n" + "\n".join(summary))
    print(f"\nReport: {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
