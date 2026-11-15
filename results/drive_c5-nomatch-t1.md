# Drive run `c5-nomatch-t1`

`python drive.py --set no_match --repeat 1 --parallel 1 --delay 0.0 --label c5-nomatch-t1` against http://127.0.0.1:8000, finished 2026-11-15T05:27:23.666+00:00.

## Summary

- requests sent: 2
- status counts: 200: 2
- requests with a log record: 2 of 2
- caller-observed latency of 200s (ms): p50 230.0, p90 455.8, max 455.8
- queue wait (ms): mean 0, max 0

## What the caller saw

| # | body | status | caller ms | request_id | outcome / error |
|---|---|---|---|---|---|
| 1 | `{"query": "designer ballgown size XXS under $5"}` | 200 | 455.8 | 1e99cff7f009 | No listings matched after FitFindr dropped the size filter f |
| 2 | `{"query": "wool sweater under $40"}` | 200 | 230.0 | b956d694ced6 | No listings matched. Try broader keywords, a different size, |

## Log records for this label (logs/requests.jsonl)

```json
{"timestamp": "2026-11-15T05:27:22.988+00:00", "request_id": "1e99cff7f009", "run_label": "c5-nomatch-t1", "route": "/ask", "query": "designer ballgown size XXS under $5", "status": 200, "outcome": "no_results", "error": "No listings matched after FitFindr dropped the size filter for XXS. Try broader keywords or a higher price limit.", "selected_item_id": null, "result_count": 0, "fit_card": null, "total_ms": 446.7, "queue_wait_ms": 0.0, "run_ms": 446.6, "stage_ms": {"parse": 0.0, "search": 226.5, "search_retry": 220.1}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T05:27:23.436+00:00", "request_id": "b956d694ced6", "run_label": "c5-nomatch-t1", "route": "/ask", "query": "wool sweater under $40", "status": 200, "outcome": "no_results", "error": "No listings matched. Try broader keywords, a different size, or a higher price limit.", "selected_item_id": null, "result_count": 0, "fit_card": null, "total_ms": 228.8, "queue_wait_ms": 0.0, "run_ms": 228.6, "stage_ms": {"parse": 0.0, "search": 228.6}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
```
