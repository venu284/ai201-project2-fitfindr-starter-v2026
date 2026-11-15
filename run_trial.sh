#!/usr/bin/env bash
# Run one capstone trial: every criterion in criteria.md, once. Capstone (unit 9).
#
#     ./run_trial.sh 1
#
# Starts the service with the RUNNING.md command, runs C1/C4 (burst), restarts
# the service after a 65 s idle so Gemini's per-minute window is clear, runs
# C2/C3 (warm-up then paced) and C5 (bad bodies, impossible queries), stops the
# service and scores the trial. Server stderr goes to results/server_tN_*.log.
set -euo pipefail

N="${1:?usage: ./run_trial.sh <trial number>}"
cd "$(dirname "$0")"
PY=.venv/bin/python
URL=http://127.0.0.1:8000
mkdir -p results

start_server() {
  AI201_CACHE=0 .venv/bin/gunicorn -w 1 -b 127.0.0.1:8000 serve:app \
    >"results/server_t${N}_$1.log" 2>&1 &
  SERVER_PID=$!
  for _ in $(seq 1 50); do
    curl -sf "$URL/health" >/dev/null && return 0
    sleep 0.2
  done
  echo "service did not start" >&2
  exit 1
}

stop_server() {
  kill "$SERVER_PID" 2>/dev/null || true
  wait "$SERVER_PID" 2>/dev/null || true
}
trap stop_server EXIT

echo "== trial $N: C1/C4 burst =="
start_server burst
$PY drive.py --set matching --repeat 2 --label "c1-burst-t${N}"
stop_server

echo "== idle 65 s so the per-minute window is clear =="
sleep 65

echo "== trial $N: C2/C3 warm-up and paced run, then C5 =="
start_server paced
curl -s -o /dev/null -w "warm-up: %{http_code} in %{time_total}s\n" -X POST "$URL/ask" \
  -H 'Content-Type: application/json' -H "X-Run-Label: c2-warmup-t${N}" \
  -d '{"query": "denim jacket under $60"}'
$PY drive.py --set matching --repeat 2 --delay 6 --label "c2-paced-t${N}"
$PY drive.py --set bad --label "c5-bad-t${N}"
$PY drive.py --set no_match --label "c5-nomatch-t${N}"
stop_server
trap - EXIT

echo
$PY score.py "$N" | tee "results/score_t${N}.txt"
