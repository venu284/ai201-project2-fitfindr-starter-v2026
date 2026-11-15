# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
`suggest_outfit` and `create_fit_card` both call the model, so one run can fail
even when the search and loop work. Requiring 4 of 5 successful runs still
expects the whole agent to work reliably.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
The loop checks an empty Python list and returns before either model-based tool
runs. This branch is deterministic, so it should behave the same in every run.

---

## 3. The selected listing reaches the outfit tool unchanged

When `search_listings` returns a non-empty list, the first result's `id` equals
both `session["selected_item"]["id"]` and the `new_item["id"]` received by
`suggest_outfit` in 5 of 5 tries.

**Why this target:**
This handoff uses session state in Python, not model output. Any mismatch means
the loop replaced or lost the listing that search selected.

---

## 4. The fit card includes the facts a shopper needs

Given a query that matches at least one listing, at least 4 of 5 returned fit
cards are non-empty strings with 2 to 4 sentences. Each passing card contains
the selected listing's platform name, matched without regard to letter case,
and its price as a dollar amount rounded to two decimal places.

**Why this target:**
The model can vary its wording, but the exact price, platform, and caption
length are part of the tool's contract. Allowing one miss accounts for model
variation without accepting consistently incomplete captions.

---

## 5. Search results respect the maximum price

Given a query with a maximum price that returns at least one match, every
listing in `session["search_results"]`, including `session["selected_item"]`,
has a `price` less than or equal to `session["parsed"]["max_price"]` in 5 of 5
tries.

**Why this target:**
Price filtering is deterministic and does not call the model. Returning even
one item over the stated limit would break a specific constraint from the
user's query.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Capstone criteria (Unit 9)

Five targets for the deployed, instrumented service, written after the M3
measurements and before the trials that score them. Criteria 1 to 4 are about
the extension (the log, the run path, the measured cost and timing); criteria
1, 4 and 5 cover failure paths. Each one is scored in 3 separate trials, with
the service started by the command in RUNNING.md
(`AI201_CACHE=0 gunicorn -w 1 -b 127.0.0.1:8000 serve:app`) and a new
`--label` per trial. The rate-limit window lives in the server process, so
before each trial I restart the service or wait at least 60 s, so that no trial
starts with a window another trial half used.

## C1. Every request the caller sends has a log record, even under a burst

Run `python drive.py --set matching --repeat 2 --label c1-burst-tN` (no delay,
one request at a time). In each of 3 trials, the driver's summary line reads
"requests with a log record: 10 of 10".

**Why this target:**
In M3 this exact run logged 8 of 10, and the two missing records were the two
failures (gunicorn killed the worker during a rate-limit sleep before
`serve.py` could write). A log that loses only the failures is the worst kind
of incomplete, so 9 of 10 would accept the M3 failure mode as passing. I test
it under the back-to-back burst rather than paced, because paced runs never
lost a record and would pass without testing anything.

## C2. Warm, paced requests return within 2.5 seconds

After starting the service, send one warm-up request with
`curl -s -X POST localhost:8000/ask -H 'Content-Type: application/json' -H 'X-Run-Label: c2-warmup-tN' -d '{"query": "denim jacket under $60"}'`,
then run `python drive.py --set matching --repeat 2 --delay 6 --label c2-paced-tN`. In
each of 3 trials, at least 9 of the 10 warm, paced requests have `total_ms` at
or below 2500 ms in `results/drive_c2-paced-tN.md`.

**Why this target:**
In the M3 paced run the p50 was about 2.0 s and the slowest normal run was
2290 ms, so 2.5 s leaves about 10% headroom over what two model calls plus MCP
search took. That headroom is small enough that a slower Gemini day can miss
it. The one allowed miss is for the rate limiter. With a 6 s delay and about
2 s per run, the driver sends roughly 15 model calls a minute, right at the
free-tier limit, and M3 had one run slowed to 5.4 s by a 3.7 s limiter wait. Two
or more misses means latency itself got worse rather than one limiter hit.

## C3. A fit-card run costs at most 1300 tokens and exactly 2 model calls

Same run as C2. In each of 3 trials, all 10 requests return
`outcome: "fit_card"`, and each of those 10 records has `model_calls` equal to
2 and `prompt_tokens + output_tokens` at or below 1300.

**Why this target:**
M3 runs used 923 to 1146 tokens. Prompt size barely moved (759 to 875), and
output varied by about 100 tokens (164 to 271), so 1300 covers normal output
variation with roughly 150 tokens to spare. A run over it means the prompt grew
or a retry added a call. In quota terms, 100 users a day at 1300 tokens is
130,000 tokens a day against the measured 104,200, so the ceiling allows about
25% growth before the daily estimate in the README is wrong. A third call is the
more expensive failure: 2 calls a run is 200 calls a day for 100 users, and 3
would be 300, 50% more of the 15-a-minute allowance spent for the same answer.
Every run has to stay under, because nothing in a normal fit-card run should
ever need a third call.

## C4. A burst gets a fit card or a clear error, never a bare 500

Same run as C1 (`--set matching --repeat 2`, no delay). That is 20 model calls,
more than the 15 a minute the free tier allows. In each of 3 trials, 10 of 10
requests come back within 65 s of caller time with status `200` and either
`outcome: "fit_card"` or `outcome: "model_error"` with a non-empty `error`
field. Zero rows have status `500`, a connection error, or "non-JSON error
body".

**Why this target:**
This is the M3 failure seen from the caller's side: requests 8 and 9 got a bare
`500` after about 30 s with no explanation. C1 checks that such a request is
logged; this one checks what the person waiting gets. 65 s is the longest a
request should need: one full 60 s rate-limit window plus one roughly 2 s run.
A caller waiting longer than that with no answer is no better off than with
the timeout. I require all 10 because a 500 on any request is the bug.

## C5. Bad input and empty searches are handled and spend no quota

Run `python drive.py --set bad --label c5-bad-tN` and
`python drive.py --set no_match --label c5-nomatch-tN`. In each of 3 trials,
4 of 4 bad bodies (`{}`, empty, whitespace-only, and a number) return `400`
with `outcome: "bad_request"`, and 2 of 2 impossible queries return
`outcome: "no_results"`. All 6 records show `model_calls: 0`.

**Why this target:**
Both branches return before any model call, so they should behave the same
every time. A malformed body or a nonsense query can never produce a fit card,
and any quota it spends is pure waste on a 15-a-minute budget. In M3 all four
bad bodies got a `400` with 0 model calls in one run (`--label m3-failures`),
and both no-match queries returned `no_results` with 0 calls (`--label
m3-nomatch`). One clean run shows the refusal works once. Three trials check
that it holds every time, and anything short of 6 of 6 means a branch that
should be deterministic is not.
