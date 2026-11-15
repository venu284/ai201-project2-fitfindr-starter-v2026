# Drive run `c5-nomatch-t4`

`python drive.py --set no_match --repeat 1 --parallel 1 --delay 0.0 --label c5-nomatch-t4` against http://127.0.0.1:8000, finished 2026-11-15T05:56:15.490+00:00.

## Summary

- requests sent: 2
- status counts: 200: 2
- requests with a log record: 2 of 2
- caller-observed latency of 200s (ms): p50 224.3, p90 443.9, max 443.9
- queue wait (ms): mean 0, max 0

## What the caller saw

| # | body | status | caller ms | request_id | outcome / error |
|---|---|---|---|---|---|
| 1 | `{"query": "designer ballgown size XXS under $5"}` | 200 | 443.9 | df3a6df9c4ac | No listings matched after FitFindr dropped the size filter f |
| 2 | `{"query": "wool sweater under $40"}` | 200 | 224.3 | 33bb9d94ee8a | No listings matched. Try broader keywords, a different size, |

## Log records for this label (logs/requests.jsonl)

```json
{"timestamp": "2026-11-15T05:56:14.829+00:00", "request_id": "df3a6df9c4ac", "run_label": "c5-nomatch-t4", "route": "/ask", "query": "designer ballgown size XXS under $5", "status": 200, "outcome": "no_results", "error": "No listings matched after FitFindr dropped the size filter for XXS. Try broader keywords or a higher price limit.", "selected_item_id": null, "result_count": 0, "fit_card": null, "total_ms": 435.3, "queue_wait_ms": 0.0, "run_ms": 435.2, "stage_ms": {"parse": 0.0, "search": 216.5, "search_retry": 218.7}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T05:56:15.265+00:00", "request_id": "33bb9d94ee8a", "run_label": "c5-nomatch-t4", "route": "/ask", "query": "wool sweater under $40", "status": 200, "outcome": "no_results", "error": "No listings matched. Try broader keywords, a different size, or a higher price limit.", "selected_item_id": null, "result_count": 0, "fit_card": null, "total_ms": 223.0, "queue_wait_ms": 0.0, "run_ms": 222.9, "stage_ms": {"parse": 0.0, "search": 222.9}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
```
