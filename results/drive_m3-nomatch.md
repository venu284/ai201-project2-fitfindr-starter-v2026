# Drive run `m3-nomatch`

`python drive.py --set no_match --repeat 1 --parallel 1 --label m3-nomatch` against http://127.0.0.1:8000, finished 2026-11-15T00:09:01.943+00:00.

## Summary

- requests sent: 2
- status counts: 200: 2
- requests with a log record: 2 of 2
- caller-observed latency of 200s (ms): p50 253.4, p90 531.4, max 531.4
- queue wait (ms): mean 0, max 0

## What the caller saw

| # | body | status | caller ms | request_id | outcome / error |
|---|---|---|---|---|---|
| 1 | `{"query": "designer ballgown size XXS under $5"}` | 200 | 531.4 | 6ee2ccdd54bc | No listings matched after FitFindr dropped the size filter f |
| 2 | `{"query": "wool sweater under $40"}` | 200 | 253.4 | 1d32a80dace5 | No listings matched. Try broader keywords, a different size, |

## Log records for this label (logs/requests.jsonl)

```json
{"timestamp": "2026-11-15T00:09:01.166+00:00", "request_id": "6ee2ccdd54bc", "run_label": "m3-nomatch", "route": "/ask", "query": "designer ballgown size XXS under $5", "status": 200, "outcome": "no_results", "error": "No listings matched after FitFindr dropped the size filter for XXS. Try broader keywords or a higher price limit.", "selected_item_id": null, "result_count": 0, "fit_card": null, "total_ms": 522.6, "queue_wait_ms": 0.0, "run_ms": 522.3, "stage_ms": {"parse": 0.0, "search": 295.6, "search_retry": 226.7}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T00:09:01.690+00:00", "request_id": "1d32a80dace5", "run_label": "m3-nomatch", "route": "/ask", "query": "wool sweater under $40", "status": 200, "outcome": "no_results", "error": "No listings matched. Try broader keywords, a different size, or a higher price limit.", "selected_item_id": null, "result_count": 0, "fit_card": null, "total_ms": 252.2, "queue_wait_ms": 0.0, "run_ms": 252.1, "stage_ms": {"parse": 0.0, "search": 252.0}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
```
