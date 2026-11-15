"""
gunicorn settings for FitFindr. Capstone (unit 9), the M6 improvement.

gunicorn reads ./gunicorn.conf.py on its own, so the start command in
RUNNING.md does not change:

    AI201_CACHE=0 gunicorn -w 1 -b 127.0.0.1:8000 serve:app

Why the timeout: gunicorn's default worker timeout is 30 s. generate.py can
legitimately sleep longer than that inside one request, either in
_wait_for_slot() when 15 calls were used this minute (up to about 60 s) or in
its retry loop after Gemini returns a 429 (capped at 65 s by _retry_delay()).
When the sleep outlasts the timeout, gunicorn kills the worker with
SystemExit, which serve.py's `except Exception` cannot catch, so the request
gets gunicorn's HTML 500 and no log record. 90 s covers the longest sleep plus
one agent run.
"""

timeout = 90
