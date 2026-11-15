# Drive run `c5-bad-t5`

`python drive.py --set bad --repeat 1 --parallel 1 --delay 0.0 --label c5-bad-t5` against http://127.0.0.1:8000, finished 2026-11-15T06:01:10.111+00:00.

## Summary

- requests sent: 4
- status counts: 400: 4
- requests with a log record: 4 of 4

## What the caller saw

| # | body | status | caller ms | request_id | outcome / error |
|---|---|---|---|---|---|
| 1 | `{}` | 400 | 12.2 | 4f2a66ad5860 | Send JSON with a 'query' field, e.g. {"query": "vintage grap |
| 2 | `{"query": ""}` | 400 | 0.7 | 881d1cebc0b8 | Send JSON with a 'query' field, e.g. {"query": "vintage grap |
| 3 | `{"query": "   "}` | 400 | 0.5 | 977c3390a6d3 | Send JSON with a 'query' field, e.g. {"query": "vintage grap |
| 4 | `{"query": 42}` | 400 | 0.5 | 942ee89aad64 | Send JSON with a 'query' field, e.g. {"query": "vintage grap |

## Log records for this label (logs/requests.jsonl)

```json
{"timestamp": "2026-11-15T06:01:10.107+00:00", "request_id": "4f2a66ad5860", "run_label": "c5-bad-t5", "route": "/ask", "query": null, "status": 400, "outcome": "bad_request", "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "selected_item_id": null, "result_count": null, "fit_card": null, "total_ms": 0.1, "queue_wait_ms": null, "run_ms": null, "stage_ms": {}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T06:01:10.108+00:00", "request_id": "881d1cebc0b8", "run_label": "c5-bad-t5", "route": "/ask", "query": "", "status": 400, "outcome": "bad_request", "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "selected_item_id": null, "result_count": null, "fit_card": null, "total_ms": 0.0, "queue_wait_ms": null, "run_ms": null, "stage_ms": {}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T06:01:10.109+00:00", "request_id": "977c3390a6d3", "run_label": "c5-bad-t5", "route": "/ask", "query": "   ", "status": 400, "outcome": "bad_request", "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "selected_item_id": null, "result_count": null, "fit_card": null, "total_ms": 0.0, "queue_wait_ms": null, "run_ms": null, "stage_ms": {}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T06:01:10.109+00:00", "request_id": "942ee89aad64", "run_label": "c5-bad-t5", "route": "/ask", "query": "42", "status": 400, "outcome": "bad_request", "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "selected_item_id": null, "result_count": null, "fit_card": null, "total_ms": 0.0, "queue_wait_ms": null, "run_ms": null, "stage_ms": {}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
```
