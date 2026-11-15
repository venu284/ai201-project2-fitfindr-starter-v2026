# Drive run `m3-failures`

`python drive.py --set bad --repeat 1 --parallel 1 --label m3-failures` against http://127.0.0.1:8000, finished 2026-11-15T00:09:01.108+00:00.

## Summary

- requests sent: 4
- status counts: 400: 4
- requests with a log record: 4 of 4

## What the caller saw

| # | body | status | caller ms | request_id | outcome / error |
|---|---|---|---|---|---|
| 1 | `{}` | 400 | 10.3 | 1cc3c30ec23c | Send JSON with a 'query' field, e.g. {"query": "vintage grap |
| 2 | `{"query": ""}` | 400 | 0.6 | 915043b1fb17 | Send JSON with a 'query' field, e.g. {"query": "vintage grap |
| 3 | `{"query": "   "}` | 400 | 0.5 | 4d2b7ce32948 | Send JSON with a 'query' field, e.g. {"query": "vintage grap |
| 4 | `{"query": 42}` | 400 | 0.5 | 3b9de625df62 | Send JSON with a 'query' field, e.g. {"query": "vintage grap |

## Log records for this label (logs/requests.jsonl)

```json
{"timestamp": "2026-11-15T00:09:01.106+00:00", "request_id": "1cc3c30ec23c", "run_label": "m3-failures", "route": "/ask", "query": null, "status": 400, "outcome": "bad_request", "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "selected_item_id": null, "result_count": null, "fit_card": null, "total_ms": 0.1, "queue_wait_ms": null, "run_ms": null, "stage_ms": {}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T00:09:01.107+00:00", "request_id": "915043b1fb17", "run_label": "m3-failures", "route": "/ask", "query": "", "status": 400, "outcome": "bad_request", "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "selected_item_id": null, "result_count": null, "fit_card": null, "total_ms": 0.0, "queue_wait_ms": null, "run_ms": null, "stage_ms": {}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T00:09:01.107+00:00", "request_id": "4d2b7ce32948", "run_label": "m3-failures", "route": "/ask", "query": "   ", "status": 400, "outcome": "bad_request", "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "selected_item_id": null, "result_count": null, "fit_card": null, "total_ms": 0.0, "queue_wait_ms": null, "run_ms": null, "stage_ms": {}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T00:09:01.108+00:00", "request_id": "3b9de625df62", "run_label": "m3-failures", "route": "/ask", "query": "42", "status": 400, "outcome": "bad_request", "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "selected_item_id": null, "result_count": null, "fit_card": null, "total_ms": 0.0, "queue_wait_ms": null, "run_ms": null, "stage_ms": {}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
```
