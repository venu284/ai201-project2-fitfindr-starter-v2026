# Drive run `c5-bad-t4`

`python drive.py --set bad --repeat 1 --parallel 1 --delay 0.0 --label c5-bad-t4` against http://127.0.0.1:8000, finished 2026-11-15T05:56:14.772+00:00.

## Summary

- requests sent: 4
- status counts: 400: 4
- requests with a log record: 4 of 4

## What the caller saw

| # | body | status | caller ms | request_id | outcome / error |
|---|---|---|---|---|---|
| 1 | `{}` | 400 | 10.3 | c5ba4df48d29 | Send JSON with a 'query' field, e.g. {"query": "vintage grap |
| 2 | `{"query": ""}` | 400 | 0.6 | a62b89fba7bd | Send JSON with a 'query' field, e.g. {"query": "vintage grap |
| 3 | `{"query": "   "}` | 400 | 0.5 | ae21b07960b3 | Send JSON with a 'query' field, e.g. {"query": "vintage grap |
| 4 | `{"query": 42}` | 400 | 0.4 | 899ee3f5582c | Send JSON with a 'query' field, e.g. {"query": "vintage grap |

## Log records for this label (logs/requests.jsonl)

```json
{"timestamp": "2026-11-15T05:56:14.769+00:00", "request_id": "c5ba4df48d29", "run_label": "c5-bad-t4", "route": "/ask", "query": null, "status": 400, "outcome": "bad_request", "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "selected_item_id": null, "result_count": null, "fit_card": null, "total_ms": 0.1, "queue_wait_ms": null, "run_ms": null, "stage_ms": {}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T05:56:14.770+00:00", "request_id": "a62b89fba7bd", "run_label": "c5-bad-t4", "route": "/ask", "query": "", "status": 400, "outcome": "bad_request", "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "selected_item_id": null, "result_count": null, "fit_card": null, "total_ms": 0.0, "queue_wait_ms": null, "run_ms": null, "stage_ms": {}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T05:56:14.770+00:00", "request_id": "ae21b07960b3", "run_label": "c5-bad-t4", "route": "/ask", "query": "   ", "status": 400, "outcome": "bad_request", "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "selected_item_id": null, "result_count": null, "fit_card": null, "total_ms": 0.0, "queue_wait_ms": null, "run_ms": null, "stage_ms": {}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T05:56:14.771+00:00", "request_id": "899ee3f5582c", "run_label": "c5-bad-t4", "route": "/ask", "query": "42", "status": 400, "outcome": "bad_request", "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "selected_item_id": null, "result_count": null, "fit_card": null, "total_ms": 0.0, "queue_wait_ms": null, "run_ms": null, "stage_ms": {}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
```
