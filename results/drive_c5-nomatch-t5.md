# Drive run `c5-nomatch-t5`

`python drive.py --set no_match --repeat 1 --parallel 1 --delay 0.0 --label c5-nomatch-t5` against http://127.0.0.1:8000, finished 2026-11-15T06:01:10.865+00:00.

## Summary

- requests sent: 2
- status counts: 200: 2
- requests with a log record: 2 of 2
- caller-observed latency of 200s (ms): p50 251.0, p90 450.4, max 450.4
- queue wait (ms): mean 0, max 0

## What the caller saw

| # | body | status | caller ms | request_id | outcome / error |
|---|---|---|---|---|---|
| 1 | `{"query": "designer ballgown size XXS under $5"}` | 200 | 450.4 | 5f4f9163827f | No listings matched after FitFindr dropped the size filter f |
| 2 | `{"query": "wool sweater under $40"}` | 200 | 251.0 | c98f4943a21f | No listings matched. Try broader keywords, a different size, |

## Log records for this label (logs/requests.jsonl)

```json
{"timestamp": "2026-11-15T06:01:10.170+00:00", "request_id": "5f4f9163827f", "run_label": "c5-nomatch-t5", "route": "/ask", "query": "designer ballgown size XXS under $5", "status": 200, "outcome": "no_results", "error": "No listings matched after FitFindr dropped the size filter for XXS. Try broader keywords or a higher price limit.", "selected_item_id": null, "result_count": 0, "fit_card": null, "total_ms": 441.4, "queue_wait_ms": 0.0, "run_ms": 441.3, "stage_ms": {"parse": 0.0, "search": 221.7, "search_retry": 219.5}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T06:01:10.613+00:00", "request_id": "c98f4943a21f", "run_label": "c5-nomatch-t5", "route": "/ask", "query": "wool sweater under $40", "status": 200, "outcome": "no_results", "error": "No listings matched. Try broader keywords, a different size, or a higher price limit.", "selected_item_id": null, "result_count": 0, "fit_card": null, "total_ms": 249.4, "queue_wait_ms": 0.0, "run_ms": 249.3, "stage_ms": {"parse": 0.0, "search": 249.3}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
```
