# Drive run `c5-nomatch-t3`

`python drive.py --set no_match --repeat 1 --parallel 1 --delay 0.0 --label c5-nomatch-t3` against http://127.0.0.1:8000, finished 2026-11-15T05:38:24.166+00:00.

## Summary

- requests sent: 2
- status counts: 200: 2
- requests with a log record: 2 of 2
- caller-observed latency of 200s (ms): p50 249.2, p90 445.3, max 445.3
- queue wait (ms): mean 0, max 0

## What the caller saw

| # | body | status | caller ms | request_id | outcome / error |
|---|---|---|---|---|---|
| 1 | `{"query": "designer ballgown size XXS under $5"}` | 200 | 445.3 | f08a4bca6170 | No listings matched after FitFindr dropped the size filter f |
| 2 | `{"query": "wool sweater under $40"}` | 200 | 249.2 | b7cb482bb3f5 | No listings matched. Try broader keywords, a different size, |

## Log records for this label (logs/requests.jsonl)

```json
{"timestamp": "2026-11-15T05:38:23.479+00:00", "request_id": "f08a4bca6170", "run_label": "c5-nomatch-t3", "route": "/ask", "query": "designer ballgown size XXS under $5", "status": 200, "outcome": "no_results", "error": "No listings matched after FitFindr dropped the size filter for XXS. Try broader keywords or a higher price limit.", "selected_item_id": null, "result_count": 0, "fit_card": null, "total_ms": 436.3, "queue_wait_ms": 0.0, "run_ms": 436.2, "stage_ms": {"parse": 0.0, "search": 216.2, "search_retry": 219.9}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T05:38:23.917+00:00", "request_id": "b7cb482bb3f5", "run_label": "c5-nomatch-t3", "route": "/ask", "query": "wool sweater under $40", "status": 200, "outcome": "no_results", "error": "No listings matched. Try broader keywords, a different size, or a higher price limit.", "selected_item_id": null, "result_count": 0, "fit_card": null, "total_ms": 247.9, "queue_wait_ms": 0.0, "run_ms": 247.8, "stage_ms": {"parse": 0.0, "search": 247.8}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
```
