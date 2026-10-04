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
