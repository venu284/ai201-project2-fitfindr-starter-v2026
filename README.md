# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> That command runs the completed agent through listing search, outfit ideas,
> and a fit-card caption.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

FitFindr takes a plain-language thrift request, including keywords, size, and
maximum price, and searches a local listings dataset. If a sized search finds
nothing, it retries once without the size filter and tells the user what it
dropped. If the search is still empty, it suggests broader keywords or a higher
price limit. Otherwise it keeps the first listing, combines it with the user's
wardrobe (or gives general advice if the wardrobe is empty), and writes a short
fit-card caption. The stretch features below add a price check and a remembered
wardrobe.

### Stretch Features

FitFindr adds all three optional stretch features:

- A fourth tool, `compare_price`, compares the selected listing with the
  median price of other listings in the same category.
- A second planning-loop branch calls that tool when several listings match
  and skips it with a clear note when exactly one listing matches.
- Style memory lets the CLI import a wardrobe once and reuse it in later
  runs until the user forgets it.

The Unit 4 extras extend that work in three measured steps:

- Register `compare_price` as a second MCP tool and route the agent's price
  comparison through MCP.
- When a search returns no listings and included a size, retry once without
  the size and tell the user that the retry dropped the size filter.
- Extract `parse_query` as a second measured improvement so tests can call the
  parser directly.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches the listings data for descriptions that match the user's keywords, optional size, and optional maximum price. It ranks keyword matches before returning them.
- **Inputs:** `description` (str), `size` (str or None), and `max_price` (float or None). A size match ignores case and allows a requested size such as `M` to match `S/M`. The maximum price includes listings at the stated price.
- **Returns:** Up to 10 matching listing dictionaries, sorted from the strongest keyword match to the weakest. Each dictionary has `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.
- **When it has nothing:** Returns an empty list.

### `suggest_outfit`

- **What it does:** Uses the selected listing and the user's wardrobe to suggest one or two outfits that name compatible items from the wardrobe.
- **Inputs:** `new_item` (dict, one listing returned by `search_listings`) and `wardrobe` (dict with an `items` list of wardrobe-item dictionaries).
- **Returns:** A non-empty string with one or two outfit ideas. When the wardrobe has items, the ideas name pieces from `wardrobe["items"]`.
- **When it has nothing:** If `wardrobe["items"]` is empty, returns a non-empty string with general styling advice for `new_item`.

### `create_fit_card`

- **What it does:** Turns an outfit suggestion and the selected listing into a short caption for a thrift find.
- **Inputs:** `outfit` (str, the result from `suggest_outfit`) and `new_item` (dict, the selected listing).
- **Returns:** A two-to-four-sentence caption that names the item, its price, and its platform once each, and describes the outfit's vibe.
- **When it has nothing:** If `outfit` is empty or contains only whitespace, returns a descriptive fallback message instead of raising an error.

### `compare_price`

- **What it does:** Compares the selected listing's price with the median price of every other listing in the same category.
- **Inputs:** `new_item` (dict, the selected listing with `id`, `category`, and numeric `price` fields).
- **Returns:** A dictionary with `status`, `category`, `item_price`, `median_price`, `difference`, `comparable_count`, and `message`. The status is `below_median`, `at_median`, or `above_median` when comparison is possible.
- **When it has nothing:** Returns the same dictionary shape with `status` set to `unavailable`, both `median_price` and `difference` set to `None`, and a message explaining why.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rules:** If `search_listings` returns an empty list and the query has a
size, retry once through MCP with the same description and maximum price but no
size filter. Store what changed in `session["search_relaxation"]`. If the retry
is also empty, store an actionable message in `session["error"]` and stop before
the model tools. An empty search with no size stops without a retry. Otherwise,
store the first result in `session["selected_item"]`. If exactly one listing
matched, skip `compare_price` and record why. If several listings matched, call
`compare_price` through MCP with the selected item. Both matching paths then
call `suggest_outfit` and `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** `agent.py::parse_query` uses shared compiled regular
expressions. It recognizes `size <value>` as the size and `under`, `below`, or
`less than` followed by a dollar amount as the maximum price. It removes those
parts from the query and uses the remaining text as the description.

**What moves through the session:** The session stores the original `query`, then
the parsed `description`, `size`, and `max_price`. `search_listings` stores its
results in `search_results`. A relaxed retry also stores its explanation in
`search_relaxation`. The first result moves to `selected_item`. The match-count
branch stores either the fourth tool's return value or the skip reason in
`price_comparison`. The selected item then passes to `suggest_outfit` with the
saved `wardrobe`. The returned string moves to `outfit_suggestion`, then
`outfit_suggestion` and `selected_item` pass to `create_fit_card`, whose result
is stored in `fit_card`.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Price:    This $18.00 listing is $3.50 below the $21.50 median for tops, based on 14 comparable listings.

  Outfit:   Here are 2 outfit ideas for the Y2K Baby Tee — Butterfly Print using items from your saved wardrobe:

**Outfit Idea 1: Y2K Streetwear Look**
* **Top:** Y2K Baby Tee — Butterfly Print
* **Bottoms:** Baggy straight-leg jeans, dark wash
* **Outerwear:** Vintage black denim jacket
* **Shoes:** Chunky white sneakers
* **Accessories:** Black crossbody bag

**Outfit Idea 2: Casual Retro Contrast**
* **Top:** Y2K Baby Tee — Butterfly Print
* **Bottoms:** Wide-leg khaki trousers
* **Accessories:** Brown leather belt and Black crossbody bag
* **Shoes:** Chunky white sneakers

  Fit card: Channel ultimate nostalgic energy with this butterfly graphic Y2K Baby Tee — Butterfly Print, perfect for pairing with baggy denim for an effortless retro streetwear vibe. Grab it now on depop for just $18.00 to complete your go-to cropped aesthetic!

0 model calls this session, 2 served from cache
```

**The four tools, tested one at a time**

```
$ .venv/bin/python -c "from tools import search_listings; matches=search_listings('vintage graphic tee', size='M', max_price=30); empty=search_listings('designer ballgown', size='XXS', max_price=5); print({'matches': [(item['id'], item['title'], item['size'], item['price']) for item in matches], 'empty': empty})"
{'matches': [('lst_002', 'Y2K Baby Tee — Butterfly Print', 'S/M', 18.0), ('lst_017', 'Mesh Long-Sleeve Top — Black', 'S/M', 15.0), ('lst_013', '90s Silk Slip Dress — Floral, Midi Length', 'M', 30.0), ('lst_020', 'Henley Long Sleeve — Washed Burgundy', 'M', 16.0), ('lst_024', 'Vintage Polo Shirt — Forest Green', 'M', 18.0), ('lst_029', 'Silk Button-Down — Sage Green', 'M', 28.0), ('lst_030', 'Vintage Knit Vest — Argyle Brown/Cream', 'M', 25.0), ('lst_038', 'Denim Vest — Medium Wash, Studded', 'M', 27.0)], 'empty': []}
```

```
$ .venv/bin/python -c "from tools import suggest_outfit; from utils.data_loader import get_empty_wardrobe, get_example_wardrobe, load_listings; item=load_listings()[1]; print('SAVED WARDROBE:'); print(suggest_outfit(item, get_example_wardrobe())); print('EMPTY WARDROBE:'); print(suggest_outfit(item, get_empty_wardrobe()))"
SAVED WARDROBE:
Here are 2 outfit ideas for the Y2K Baby Tee — Butterfly Print using items from your saved wardrobe:

**Outfit Idea 1: Y2K Streetwear Look**
* **Top:** Y2K Baby Tee — Butterfly Print
* **Bottoms:** Baggy straight-leg jeans, dark wash
* **Outerwear:** Vintage black denim jacket
* **Shoes:** Chunky white sneakers
* **Accessories:** Black crossbody bag

**Outfit Idea 2: Casual Retro Contrast**
* **Top:** Y2K Baby Tee — Butterfly Print
* **Bottoms:** Wide-leg khaki trousers
* **Accessories:** Brown leather belt and Black crossbody bag
* **Shoes:** Chunky white sneakers
EMPTY WARDROBE:
Here is some general styling advice for this Y2K butterfly baby tee, along with clothing, shoe, and accessory suggestions to build a complete look around the item:

### Styling Vibe
Since this piece bridges the gap between Y2K pop culture and soft cottagecore, you can lean into either aesthetic depending on the mood. The fitted, cropped silhouette looks best balanced with either low-rise bottoms (for true Y2K nostalgia) or flowy, high-waisted pieces (to play up the cottagecore tag).

### Clothing Pairings
*   **Bottoms:**
    *   Low-rise, wide-leg cargo pants or parachute pants in beige, white, or pastel pink to emphasize the 2000s street style.
    *   A denim cargo miniskirt or a pleated tennis skirt for a playful, school-girl Y2K look.
    *   A flowy, tiered midi skirt in white or floral print to lean into the cottagecore aesthetic.
    *   Classic low-rise flare jeans with a slight wash.
*   **Outerwear:**
    *   A white zip-up hoodie or a cropped pastel cardigan left unbuttoned.
    *   A faux-fur trim jacket for extra early-2000s pop star energy.

### Shoe Suggestions
*   Platform sandals or chunky slide sandals.
*   Retro-style sneakers (like chunky skate shoes or pastel-accented trainers).
*   Strappy kitten-heel sandals for a dressed-up casual look.
*   Strappy flat sandals if leaning toward the cottagecore vibe.

### Accessories
*   **Bags:** A small nylon shoulder bag (baguette bag), a beaded mini handbag, or a canvas crossbody bag.
*   **Jewelry:** Layered silver or beaded choker necklaces, butterfly hair clips (claws or butterfly pins), and hoop earrings.
*   **Extras:** Rimless tinted sunglasses (pink or purple gradient lenses) and a pastel claw clip for an easy updo.
```

```
$ .venv/bin/python -c "import config; config.CACHE_ENABLED=False; from tools import create_fit_card; from utils.data_loader import load_listings; item=load_listings()[1]; outfit='Baggy straight-leg jeans, dark wash with the Vintage black denim jacket and Chunky white sneakers.'; cards=[create_fit_card(outfit, item) for _ in range(3)]; print('CARD 1:'); print(cards[0]); print('CARD 2:'); print(cards[1]); print('CARD 3:'); print(cards[2]); print('EMPTY OUTFIT:'); print(create_fit_card('   ', item))"
CARD 1:
Channel pure early-2000s pop star energy by pairing this Y2K Baby Tee — Butterfly Print with baggy dark-wash jeans and chunky kicks. It's the ultimate nostalgic, effortless street style look for everyday wear. Snag this nostalgic top right now on depop for just $18.00!
CARD 2:
Channel nostalgic early 2000s energy with this dreamy Y2K Baby Tee — Butterfly Print, paired effortlessly with baggy dark-wash jeans, a distressed black denim jacket, and chunky white sneakers. Score this ultimate vintage graphic top for just $18.00 right now on depop. It's the ultimate low-effort, high-impact fit for effortless everyday styling.
CARD 3:
Channel major pop-princess energy with this Y2K Baby Tee — Butterfly Print paired with baggy dark-wash denim and chunky white sneakers. Grab this nostalgic piece for just $18.00 over on depop to complete your ultimate retro streetwear fit.
EMPTY OUTFIT:
I couldn't create a fit card because the outfit suggestion was empty.
```

```
$ .venv/bin/python -c "from tools import compare_price; from utils.data_loader import load_listings; item=next(x for x in load_listings() if x['id']=='lst_002'); print(compare_price(item))"
{'status': 'below_median', 'category': 'tops', 'item_price': 18.0, 'median_price': 21.5, 'difference': -3.5, 'comparable_count': 14, 'message': 'This $18.00 listing is $3.50 below the $21.50 median for tops, based on 14 comparable listings.'}
```

**Second branch: one matching listing**

Relevant lines from the real terminal output:

```
$ .venv/bin/python app.py ask 'argyle'

  Found:    Vintage Knit Vest — Argyle Brown/Cream — $25.0 on thredUp

  Price:    Only one listing matched, so FitFindr skipped price comparison.

  Fit card: Channel your inner scholar with this moody dark academia fit, built around a cozy Vintage Knit Vest — Argyle Brown/Cream layered over a crisp tank and paired with wide-leg trousers. Snag this preppy earth-toned essential for just $25.00 before it finds a new semester on thredUp!

2 model calls this session, 845 prompt + 227 output tokens
```

**Style memory across separate runs**

Relevant lines from the real terminal output:

```
$ .venv/bin/python app.py wardrobe remember data/remembered_wardrobe.example.json
Remembered 2 wardrobe items in .fitfindr/wardrobe.json.

$ .venv/bin/python app.py ask 'denim jacket under $50'
(using remembered wardrobe with 2 items)

  Found:    Denim Jacket — Light Wash, Cropped — $42.0 on poshmark

  Price:    This $42.00 listing is $2.00 above the $40.00 median for outerwear, based on 7 comparable listings.

  Outfit:   **Outfit Idea 1: Casual Streetwear**
*   Outerwear: Denim Jacket — Light Wash, Cropped
*   Bottoms: Emerald pleated trousers
*   Shoes: Cream canvas sneakers

$ .venv/bin/python app.py wardrobe forget
Forgot the remembered wardrobe. Future asks will use the example wardrobe.
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I gave AI all five acceptance criteria and asked it to
  explain exactly how it would test each one using only what the criterion said.
- *What came back:* The review found that the fit-card criterion did not define
  its observable facts tightly enough, so different reviewers could score the
  same output differently.
- *What I changed:* I required a non-empty two-to-four-sentence card containing
  the selected listing's platform and its price with two decimal places in at
  least four of five tries.

**Moment 2**

- *What I asked for:* I asked AI to review `create_fit_card` and its fallback
  against the tool contract.
- *What came back:* It found that an outfit containing periods or exclamation
  marks could make the fallback longer than two sentences.
- *What I changed:* I added a regression check
  (`tests/test_fit_card_fallback.py`) and normalized sentence-ending
  punctuation in the outfit before constructing the two-sentence fallback.

**Moment 3**

- *What I asked for:* I asked AI to argue against my five criterion verdicts
  using the original targets and all 25 before-run results, then to recommend
  one improvement from the weakest point it found.
- *What came back:* It found no mis-scored pass, but it pointed out that the
  model could still return a nonempty fit card without the exact price or
  platform. The repeated evaluation also covered only one selected listing.
- *What I changed:* I first added a test that forced a two-sentence response
  with no price or platform and watched it fail. I then added the
  `create_fit_card` contract check, ran the same 25 tries with the rate limiter
  unchanged, and reported that every score stayed at 5 of 5.

**Moment 4 — Unit 4 stretch review**

- *What I asked for:* I asked two independent AI reviews to check the second
  MCP move, the size-relaxation branch, and the parser refactor against the
  published tool contracts and tests.
- *What came back:* The reviews found gaps in the `compare_price` MCP contract
  documentation and in retry tests for the exhausted and successful paths.
- *What I changed:* I documented `compare_price` inputs, result fields, and
  `unavailable` behavior; added direct-versus-MCP parity tests; and added tests
  for one retry, exhausted retries, the displayed retry message, and parser
  cases.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected listing reaches the outfit tool unchanged | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card includes the shopper facts | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Search respects the maximum price | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

I ran the five scenarios in `scenarios.py` with
`.venv/bin/python run_eval.py --label before`. Caching was off. The run made
40 model calls, and the returned fit cards varied between tries. The complete
output for all 25 tries is in
[`results/run_2026-10-11_0032_before.md`](results/run_2026-10-11_0032_before.md).
The excerpts below come from `run_eval.py::run_once`, which calls
`agent.py::run_agent` and records its session and trace.

**Criterion 1, try 1.** The trace shows the search, outfit, and fit-card calls;
the session contains a fit card.

```
- stopped early: no
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
- search_results: 10
Fit card:
Channel serious early 2000s energy with this dreamy butterfly-printed crop, perfect for serving nostalgic streetwear or edgy contrast looks. Snag this nostalgic piece for just $18.00 and start styling your dream aesthetic today. You can find this exact top listed right now on depop!
[2] search_listings (via MCP)
[5] suggest_outfit
[6] create_fit_card
```

**Criterion 2, try 1.** The empty result ends the trace before
`suggest_outfit`.

```
- stopped early: yes — No listings matched. Try broader keywords, a different size, or a higher price limit.
- search_results: 0
[2] search_listings (via MCP)
      in:  description='designer ballgown', size='XXS', max_price=5.0
      out: [] (empty)
[3] search_results branch
      in:  0 matches
      out: No listings matched. Try broader keywords, a different size, or a higher price limit.
      →    stop
```

**Criterion 3, try 1.** The first search result, selected item, and outfit
tool input all carry the same ID.

```
- first_search_result_id: 'lst_002'
- selected_item_id: 'lst_002'
[5] suggest_outfit
      in:  new_item_id=lst_002, wardrobe_items=10, first_item='Baggy straight-leg jeans, dark wash'
```

**Criterion 4, try 1.** The selected listing is from `depop` at `$18.00`;
the returned card has three sentences and includes both facts.

```
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
Fit card:
Channel peak nostalgic energy with this dreamy butterfly-printed crop that effortlessly bridges casual streetwear and soft pastel whimsy. Style it with baggy denim and chunky sneakers for the ultimate low-effort, high-impact fit. Snag this Y2K Baby Tee — Butterfly Print right now for $18.00 exclusively over on depop!
```

**Criterion 5, try 1.** The report lists every returned price, including one
at the inclusive `$30.00` limit.

```
- first_search_result_id: 'lst_002'
- selected_item_id: 'lst_002'
- parsed_max_price: 30.0
- search_result_id_prices: [('lst_002', 18.0), ('lst_006', 24.0), ('lst_033', 19.0), ('lst_015', 26.0), ('lst_017', 15.0), ('lst_003', 22.0), ('lst_011', 27.0), ('lst_012', 20.0), ('lst_013', 30.0), ('lst_014', 12.0)]
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes all three tools | 4 of 5 | MET (5/5) | Each try called `search_listings`, `suggest_outfit`, and `create_fit_card` and returned a fit card. |
| 2 | Impossible query stops before the second tool | 5 of 5 | MET (5/5) | Each search returned no listings; the loop stopped before `suggest_outfit` and told the user to broaden keywords, change size, or raise the price limit. |
| 3 | Selected listing reaches the outfit tool unchanged | 5 of 5 | MET (5/5) | In every try, the first search result, `session["selected_item"]`, and the `new_item` passed to `suggest_outfit` had ID `lst_002`. |
| 4 | Fit card includes the shopper facts | 4 of 5 | MET (5/5) | All five cards were nonempty, had three sentences, named `depop`, and showed the selected item's price as `$18.00`. |
| 5 | Search results respect the maximum price | 5 of 5 | MET (5/5) | Every result and the selected item cost at most the parsed `$30.00` limit in every try; one result cost exactly `$30.00`. |

**Diagnoses**

No criterion missed its filed target in these 25 tries, so there is no failed
tool, loop branch, session handoff, or model output to diagnose. Four matching
scenarios repeated the same query and selected `lst_002` each time. These
results do not show how the agent performs across other listings or platforms.

Criterion 4 is the target I would tighten in a future test: 4 of 5 permits one
card to omit a price or platform that a shopper needs. I would require 5 of 5
across several selected listings and platforms. I have not changed this unit's
original criterion or rescored the before run.

---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

The traces in this section are the required Milestone 2 evidence captured before
the optional stretch work. The current two-MCP-tool and retry traces appear in
the [Unit 4 stretch evidence](#unit-4-stretch-evidence) section.

**Historical happy path**

```
$ .venv/bin/python app.py ask 'vintage graphic tee under $30' --trace
[1] parse_query
      in:  vintage graphic tee under $30
      out: description='vintage graphic tee', size=None, max_price=30.0
[2] search_listings (via MCP)
      in:  description='vintage graphic tee', size=None, max_price=30.0
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[3] select_item
      in:  first of 10 matches
      out: id=lst_002, title=Y2K Baby Tee — Butterfly Print
[4] compare_price
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: This $18.00 listing is $3.50 below the $21.50 median for tops, based on 14 comparable listings.
[5] suggest_outfit
      in:  new_item_id=lst_002, wardrobe_items=10, first_item='Baggy straight-leg jeans, dark wash'
      out: Here are 2 outfit ideas for the Y2K Baby Tee — Butterfly Print using items from your saved wardrobe:  **Outfit…
[6] create_fit_card
      in:  new_item_id=lst_002, outfit=Here are 2 outfit ideas for the Y2K Baby Tee — Butterfly Print using items from yo…
      out: Channel ultimate nostalgic energy with this butterfly graphic Y2K Baby Tee — Butterfly Print, perfect for pair…
```

The full query returned the selected listing, price comparison, outfit, and
fit card. Its two model responses came from the build cache; the MCP search
and loop still ran for this query.

**Historical empty search**

```
$ .venv/bin/python app.py ask 'designer ballgown size XXS under $5' --trace
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: description='designer ballgown', size='XXS', max_price=5.0
[2] search_listings (via MCP)
      in:  description='designer ballgown', size='XXS', max_price=5.0
      out: [] (empty)
[3] search_results branch
      in:  0 matches
      out: No listings matched. Try broader keywords, a different size, or a higher price limit.
      →    stop

  No listings matched. Try broader keywords, a different size, or a higher price limit.
```

**Failure checks**

In this pre-stretch run, the empty-search message named three constraints the
user could change and no model tool ran. The current sized-search behavior
retries once without size, as shown in the stretch evidence below.

With `--empty-wardrobe`, the CLI said `(running with an empty wardrobe)` and
`suggest_outfit` returned general advice rather than stopping. An excerpt of
the returned advice is:

```
Here is general styling advice for the light wash, cropped denim jacket from Wrangler:

### Clothing Pairings
*   **High-Waisted Bottoms:** Since the jacket is cropped, pairing it with high-waisted mom jeans, straight-leg trousers, or a high-rise midi skirt helps balance proportions and defines the waist.
```

That run produced a fit card too. The first run made two model calls; a repeated
check returned the same response from the build cache.

For model unavailability, I set an invalid key only for one process and turned
the build cache off. The real `.env` file was not edited. The model rejected
the key, and `run_agent` returned this message without a traceback:

```
$ GEMINI_API_KEY=invalid-milestone2-check AI201_CACHE=0 .venv/bin/python app.py ask 'plaid flannel shirt size XL under $29 for milestone two key check' --trace
The model couldn't be reached while suggesting an outfit. Check GEMINI_API_KEY and your internet connection, then try again.
```

The trace for that run ended at `suggest_outfit`. Its `create_fit_card` step was
not called. A matching handler covers a model failure during fit-card creation.

**On the MCP move:** `search_listings` is registered in `mcp_server.py` with
`description: str`, optional `size: str`, and optional `max_price: float` in
dollars. `agent.py::run_agent` calls it through `mcp_client.call_tool`; the
same route now calls `compare_price`. Both deterministic tools use MCP;
`suggest_outfit` and `create_fit_card` remain direct model calls. `python
mcp_client.py` listed the registered tools and their input schemas. A
direct-versus-MCP check returned equal search lists for a matching query and an
empty search. Behavior did not change after the move: a normal `app.py ask`
query still returned the Y2K Baby Tee, the price comparison, an outfit
suggestion, and a fit card. That full run used cached model responses.


---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

`tools.py::create_fit_card` now checks every model response before returning
it. A passing response has two to four sentences and contains the selected
listing's exact two-decimal price and platform once each. If the response
misses any check, the tool returns its existing deterministic fallback without
making another model call.

**Which failure it was meant to fix:**

The before run had no observed miss, but criterion 4 depends on unconstrained
model output and its 4-of-5 target permits one card to omit a shopper fact.
The new check closes that gap at the tool boundary. A regression test forces a
nonempty response with no price or platform and confirms that the tool rejects
it.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected listing reaches the outfit tool unchanged | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card includes the shopper facts | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Search respects the maximum price | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Did it help, and how do I know:**

The measured scores did not change: every criterion scored 5 of 5 before and
after. The new regression test shows the narrower improvement. Before the
change, `create_fit_card` returned a nonempty two-sentence response that omitted
both `$18.00` and `depop`; after the change, the same response produces the
contract-compliant fallback.

The after run used the same scenarios with caching off. It completed 25 tries
and made 40 model calls while the built-in 15-request-per-minute limiter paced
the run. The complete output is in
[`results/run_2026-10-11_1042_after.md`](results/run_2026-10-11_1042_after.md).

**Criterion 4, try 1 output:**

```
Channel peak early 2000s energy with this dreamy butterfly graphic tee, styled effortlessly for casual vintage coffee runs or nostalgic streetwear nights. Snag the Y2K Baby Tee — Butterfly Print for $18.00 and lock down your ultimate retro aesthetic. Grab it now exclusively on depop!
```


## Unit 4 stretch evidence

### Second MCP move

`agent.py::run_agent` calls both `search_listings` and `compare_price` through
`mcp_client.call_tool`. The model tools, `suggest_outfit` and `create_fit_card`,
remain direct calls. `mcp_server.py::compare_price` advertises one required
`new_item` object. Its description says that `id` excludes the selected
listing, and `category` plus numeric `price` enable comparison. It names the
stable result fields and `status="unavailable"` when it cannot compare a
listing.

`tests/test_mcp_search.py` compares direct and MCP `compare_price` results for
both a normal listing and an unavailable listing. It also inspects MCP tool
discovery. The route changes, but those results do not: the parity tests pass.

### Size-relaxation retry

The loop retries only when the first MCP `search_listings` call returns an
empty list and the parsed query has a size. It retries exactly once with
`size=None`; the description and maximum price stay unchanged. If that retry
finds listings, the query continues. This real successful-retry trace came
from `.venv/bin/python app.py ask 'argyle size S under $30' --trace`:

```
[2] search_listings (via MCP)
      in:  description='argyle', size='S', max_price=30.0
      out: [] (empty)
[3] search_listings retry (via MCP)
      in:  description='argyle', size=None, max_price=30.0
      out: 1 items: Vintage Knit Vest — Argyle Brown/Cream
      →    dropped size filter
[4] search relaxation
      out: No listings matched size S, so FitFindr retried without the size filter.
[5] select_item
      out: id=lst_030, title=Vintage Knit Vest — Argyle Brown/Cream
[6] compare_price (skipped)
      out: Only one listing matched, so FitFindr skipped price comparison.
[7] suggest_outfit
      in:  new_item_id=lst_030, wardrobe_items=10
[8] create_fit_card
      in:  new_item_id=lst_030, outfit=**Outfit Idea 1: Dark Academia Preppy** …

  No listings matched size S, so FitFindr retried without the size filter.
  Found:    Vintage Knit Vest — Argyle Brown/Cream — $25.0 on thredUp
```

The CLI prints the retry notice before `Found:`. The first run had no cached
responses for this query and made 2 model calls.

If the retry is also empty, the user sees: `No listings matched after FitFindr
dropped the size filter for XXS. Try broader keywords or a higher price limit.`
The new evaluation reports show the exhausted branch:

```
[3] search_listings retry (via MCP)
      in:  description='designer ballgown', size=None, max_price=5.0
      out: [] (empty)
      →    dropped size filter
[4] search relaxation
      out: No listings matched size XXS, so FitFindr retried without the size filter.
[5] search_results branch
      in:  0 matches after retry
      out: No listings matched after FitFindr dropped the size filter for XXS. Try broader keywords or a higher price lim…
      →    stop
```

### Second improvement: query parsing

Earlier feedback identified duplicated inline regular expressions in
`run_agent` and no way to test parsing directly. `agent.py::parse_query` now
uses compiled shared `SIZE_PATTERN` and `PRICE_PATTERN` values to extract size
and maximum price, then removes the matched constraints to produce the
description. `tests/test_query_parsing.py` calls the public helper directly for
sizes, all supported price phrases, mixed constraints, case, and decimals.

### Stretch evaluations

Both evaluations ran 25 tries with caching off. I scored every result against
the unchanged criteria. For criterion 4, each of the five cards in each report
is nonempty, has two or three sentences, includes `depop` without regard to
case, and includes `$18.00`. For criterion 5, every listed price, including
the selected item, is at most the parsed `$30.00` limit.

| Criterion | Target | Stretch before improvement | Stretch after improvement |
|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS, PASS, PASS, PASS, PASS — MET (5/5) | PASS, PASS, PASS, PASS, PASS — MET (5/5) |
| 2. Impossible query stops before the second tool | 5 of 5 | PASS, PASS, PASS, PASS, PASS — MET (5/5) | PASS, PASS, PASS, PASS, PASS — MET (5/5) |
| 3. Selected listing reaches the outfit tool unchanged | 5 of 5 | PASS, PASS, PASS, PASS, PASS — MET (5/5) | PASS, PASS, PASS, PASS, PASS — MET (5/5) |
| 4. Fit card includes the shopper facts | 4 of 5 | PASS, PASS, PASS, PASS, PASS — MET (5/5) | PASS, PASS, PASS, PASS, PASS — MET (5/5) |
| 5. Search respects the maximum price | 5 of 5 | PASS, PASS, PASS, PASS, PASS — MET (5/5) | PASS, PASS, PASS, PASS, PASS — MET (5/5) |

The console reported 42 provider calls, including retries, for the
[stretch-before-improvement report](results/run_2026-10-11_2040_stretch-before-improvement.md).
The console reported 40 model calls for the
[stretch-after-improvement report](results/run_2026-10-11_2048_stretch-after-improvement.md)
run. The scores stayed identical, so the parse refactor did not improve this
fixed evaluation rate. Its evidence is structural instead:
direct parser tests cover the extracted helper, and MCP parity tests preserve
the old deterministic behavior.



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->

No criterion missed its target in the after run. The evaluation still repeats
one matching query and selects `lst_002` on every matching path, so it does not
show whether the fit-card check behaves consistently across other prices,
platforms, or listing text. The focused regression test covers one deliberately
incomplete model response, not every malformed response a model could produce.
I stopped there because this unit allowed one system improvement and required
the same scenarios before and after. Adding more validators or changing the
scenario inputs would make it harder to attribute the measured result to that
one change.

## Submission

Repository URL, unchanged from the previous unit:
[github.com/venu284/ai201-project2-fitfindr-starter-v2026](https://github.com/venu284/ai201-project2-fitfindr-starter-v2026)


<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**

---

## Capstone

Unit 9. Everything above this heading is the Unit 3 and Unit 4 submission and
is left as it was. Every section for this unit is below.

**What This Extends**

This extends FitFindr, my Unit 3/4 thrift-shopping agent. Before this unit,
FitFindr only ran as a command (`python app.py ask ...`) or through a bare
`serve.py` with no record of what it did. What's new is an operational layer
around the HTTP service:

- every `/ask` request, including the ones that fail, writes one structured
  JSON line to `logs/requests.jsonl`
- each record carries end-to-end latency, how long the request waited for the
  one-at-a-time lock, time spent in each agent stage, model calls, tokens, cache
  hits, and time spent waiting on the rate limiter
- a single documented `gunicorn` command that starts the service outside my
  editor
- a request driver that replays a fixed set of queries against the running
  service, so cost and latency come from measured runs

The agent's tools, planning loop and prompts don't change.

**The Shape**

Shape A, deploy and instrument. The extension is the run path, the structured
log, and the numbers that come out of it: latency, per-stage time, tokens per
run, and what happens when requests fail or overlap.

Out of scope:

- I am not adding a browser front end. The service stays JSON over HTTP.
- I am not changing the tools, the planning loop, the prompts or the listings
  data. Anything I find wrong with them goes in What's Still Broken, unless it
  is the one improvement.
- I am not hosting it. I chose Path B (local with logs), so there is no cloud
  account, container or host config.
- I am not adding concurrency. `serve.py` keeps running one agent at a time,
  because MCP starts a subprocess per call and `generate.py`'s rate limiter is
  process-global.

Stretch, declared before building: **a latency breakdown**, meaning measured
time per stage (parse, MCP search, MCP price comparison, `suggest_outfit`,
`create_fit_card`) for each run.

**Running It**

Path B, local with logs. The service runs on my machine under gunicorn, started
by one command:

```bash
AI201_CACHE=0 gunicorn -w 1 -b 127.0.0.1:8000 serve:app
```

The environment it needs, the setup from a clean checkout, how to check it and
how to replay the fixed query sets are all in the Capstone section of
[RUNNING.md](RUNNING.md). I tested those instructions by cloning this repository
into an empty folder, creating a fresh virtual environment, and following them
exactly: the service started, `/health` answered, a real `/ask` returned a fit
card for `lst_007`, and the request appeared in `logs/requests.jsonl`. The run
record is committed in [logs/requests.jsonl](logs/requests.jsonl), and each
driver run writes a report to `results/drive_<label>.md`.

**Instrumentation**

`serve.py::ask` writes one JSON object per request to `logs/requests.jsonl`
through `runlog.py::write_record`, on every path: a successful fit card, an
empty search, a model error, a rejected body (400) and a crash (500). Each
record holds:

- **when and which**: `timestamp` (UTC, milliseconds), `request_id` (also sent
  back in the `X-Request-Id` header), `run_label` (from the `X-Run-Label`
  header, so one test run's requests can be pulled out)
- **what came in**: `query`
- **what came out**: `status`, `outcome` (`fit_card`, `no_results`,
  `model_error`, `bad_request`, `server_error`), `error`, `selected_item_id`,
  `result_count`, `fit_card`
- **how long it took**: `total_ms` end to end in the service, split into
  `queue_wait_ms` (waiting for another request to finish) and `run_ms` (inside
  `run_agent`), plus `stage_ms` per agent stage (`parse`, `search`,
  `search_retry`, `compare_price`, `suggest_outfit`, `create_fit_card`), timed
  by `agent.py::_timed`
- **what it used**: `model_calls`, `cache_hits`, `prompt_tokens`,
  `output_tokens` and `rate_limit_wait_s`, taken as the difference of
  `generate.py::counters()` before and after the run
- **configuration**: `model`, `cache_enabled`

Fourteen entries from the M3 session on 2026-11-14 (local time, the log is in
UTC): ten paced fit-card runs (`python drive.py --set matching --repeat 2
--delay 6 --label m3-cost-paced`), two rejected bodies (`--set bad`) and two
empty searches (`--set no_match`):

```json
{"timestamp": "2026-11-15T00:09:13.980+00:00", "request_id": "b70f4927ad6b", "run_label": "m3-cost-paced", "route": "/ask", "query": "vintage graphic tee under $30", "status": 200, "outcome": "fit_card", "error": null, "selected_item_id": "lst_002", "result_count": 10, "fit_card": "Channel nostalgic early 2000s energy by pairing this butterfly baby tee with baggy dark-wash denim and chunky white sneakers for the ultimate casual street look. You can also throw on an edgy black denim jacket and combat boots to contrast the sweet pastel graphics. Score this nostalgic top for just $18.00 exclusively on depop today!", "total_ms": 1825.5, "queue_wait_ms": 0.0, "run_ms": 1825.4, "stage_ms": {"parse": 0.0, "search": 222.3, "compare_price": 221.5, "suggest_outfit": 827.8, "create_fit_card": 553.7}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 822, "output_tokens": 216, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T00:09:21.815+00:00", "request_id": "b9bce97122b0", "run_label": "m3-cost-paced", "route": "/ask", "query": "denim jacket under $60", "status": 200, "outcome": "fit_card", "error": null, "selected_item_id": "lst_007", "result_count": 7, "fit_card": "Channel effortless off-duty model energy with this structured light wash cropped denim jacket, perfect for building a high-contrast minimalist silhouette or leaning into full streetwear nostalgia. You can grab this versatile vintage staple for $42.00 over on poshmark right now. It's the ultimate clean slate ready to be styled into your go-to everyday rotation.", "total_ms": 1979.2, "queue_wait_ms": 0.0, "run_ms": 1978.8, "stage_ms": {"parse": 0.0, "search": 255.7, "compare_price": 226.9, "suggest_outfit": 780.7, "create_fit_card": 715.4}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 807, "output_tokens": 221, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T00:09:29.805+00:00", "request_id": "472018d98ee3", "run_label": "m3-cost-paced", "route": "/ask", "query": "floral dress under $35", "status": 200, "outcome": "fit_card", "error": null, "selected_item_id": "lst_013", "result_count": 1, "fit_card": "Channel effortless 90s indie sleaze by layering this floral midi with a cozy crewneck and edgy combat boots, or keep it casual with a classic black denim jacket and chunky sneakers. Grab this vintage silk slip dress for just $30.00 before it's gone. Find it listed now on depop!", "total_ms": 1958.9, "queue_wait_ms": 0.0, "run_ms": 1958.2, "stage_ms": {"parse": 0.0, "search": 261.7, "suggest_outfit": 999.7, "create_fit_card": 696.7}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 871, "output_tokens": 242, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T00:09:37.772+00:00", "request_id": "65d3945e0c35", "run_label": "m3-cost-paced", "route": "/ask", "query": "leather bag", "status": 200, "outcome": "fit_card", "error": null, "selected_item_id": "lst_039", "result_count": 4, "fit_card": "Channel effortless off-duty model energy with this casual streetwear look featuring an oversized grey crewneck and baggy dark denim. Add the Mini Shoulder Bag — Tan Leather to anchor the fit with a touch of classic 90s structure. Grab this vintage gem for $38.00 before it drops on poshmark!", "total_ms": 1880.2, "queue_wait_ms": 0.0, "run_ms": 1879.6, "stage_ms": {"parse": 0.0, "search": 274.3, "compare_price": 223.8, "suggest_outfit": 687.2, "create_fit_card": 694.1}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 794, "output_tokens": 200, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T00:09:45.658+00:00", "request_id": "282eafe4dd17", "run_label": "m3-cost-paced", "route": "/ask", "query": "flannel shirt under $25", "status": 200, "outcome": "fit_card", "error": null, "selected_item_id": "lst_003", "result_count": 2, "fit_card": "Channel peak 90s attitude with this effortlessly cool grunge streetwear fit featuring chunky combat boots and relaxed denim. Snag this oversized red and black plaid piece for just $22.00 to complete your layering rotation. You can find this exact top ready to style right now on thredUp.", "total_ms": 2173.6, "queue_wait_ms": 0.0, "run_ms": 2173.1, "stage_ms": {"parse": 0.0, "search": 259.2, "compare_price": 240.7, "suggest_outfit": 983.9, "create_fit_card": 689.3}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 875, "output_tokens": 271, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T00:09:53.840+00:00", "request_id": "5e4d6e4720ab", "run_label": "m3-cost-paced", "route": "/ask", "query": "vintage graphic tee under $30", "status": 200, "outcome": "fit_card", "error": null, "selected_item_id": "lst_002", "result_count": 10, "fit_card": "Channel your inner 2000s pop princess by pairing this butterfly print baby tee with baggy dark-wash denim and chunky white sneakers for the ultimate casual streetwear vibe. You can easily score this nostalgic piece for just $18.00 over on depop. It's the absolute cutest find for building an effortlessly sweet yet edgy wardrobe.", "total_ms": 1904.5, "queue_wait_ms": 0.0, "run_ms": 1904.0, "stage_ms": {"parse": 0.0, "search": 253.9, "compare_price": 225.8, "suggest_outfit": 671.6, "create_fit_card": 752.7}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 821, "output_tokens": 215, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T00:10:01.754+00:00", "request_id": "c5457a989217", "run_label": "m3-cost-paced", "route": "/ask", "query": "denim jacket under $60", "status": 200, "outcome": "fit_card", "error": null, "selected_item_id": "lst_007", "result_count": 7, "fit_card": "Channel effortless 90s nostalgia by pairing this structured light wash cropped denim jacket with a crisp white tank, baggy dark wash denim, and chunky sneakers for the ultimate off-duty streetwear look. Grab this blank-canvas vintage staple for $42.00 on poshmark before someone else snags it!", "total_ms": 1772.8, "queue_wait_ms": 0.0, "run_ms": 1772.3, "stage_ms": {"parse": 0.0, "search": 250.7, "compare_price": 226.2, "suggest_outfit": 681.6, "create_fit_card": 613.8}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 759, "output_tokens": 164, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T00:10:09.538+00:00", "request_id": "1ce5ecaa4622", "run_label": "m3-cost-paced", "route": "/ask", "query": "floral dress under $35", "status": 200, "outcome": "fit_card", "error": null, "selected_item_id": "lst_013", "result_count": 1, "fit_card": "Channel effortless 90s grunge-chic by layering this floral silk slip dress under an oversized crewneck and chunky combat boots. You can snag this vintage midi for just $30.00 right now over on depop.", "total_ms": 5453.9, "queue_wait_ms": 0.0, "run_ms": 5453.1, "stage_ms": {"parse": 0.0, "search": 259.3, "suggest_outfit": 999.0, "create_fit_card": 4194.7}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 851, "output_tokens": 203, "rate_limit_wait_s": 3.73, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T00:10:21.001+00:00", "request_id": "60359742c34a", "run_label": "m3-cost-paced", "route": "/ask", "query": "leather bag", "status": 200, "outcome": "fit_card", "error": null, "selected_item_id": "lst_039", "result_count": 4, "fit_card": "Channel effortless vintage streetwear energy with this structured tan leather Mini Shoulder Bag. It’s the ultimate Y2K accessory to sling over an oversized crewneck and baggy denim for a cool, lived-in look. Grab this classic camel piece for $38.00 exclusively on poshmark!", "total_ms": 2290.1, "queue_wait_ms": 0.0, "run_ms": 2289.5, "stage_ms": {"parse": 0.0, "search": 256.5, "compare_price": 223.8, "suggest_outfit": 1131.0, "create_fit_card": 678.1}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 793, "output_tokens": 194, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T00:10:29.298+00:00", "request_id": "f8ce034d8fc4", "run_label": "m3-cost-paced", "route": "/ask", "query": "flannel shirt under $25", "status": 200, "outcome": "fit_card", "error": null, "selected_item_id": "lst_003", "result_count": 2, "fit_card": "Channel the ultimate 90s anti-fashion energy by pairing this slouchy red-and-black plaid top with baggy denim and combat boots for a heavy dose of effortless grunge streetwear. Snag this versatile layering essential on thredUp for just $22.00 to instantly anchor your cool-girl transitional wardrobe.", "total_ms": 2184.2, "queue_wait_ms": 0.0, "run_ms": 2183.4, "stage_ms": {"parse": 0.0, "search": 274.3, "compare_price": 222.6, "suggest_outfit": 868.5, "create_fit_card": 817.9}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 850, "output_tokens": 251, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T00:09:01.106+00:00", "request_id": "1cc3c30ec23c", "run_label": "m3-failures", "route": "/ask", "query": null, "status": 400, "outcome": "bad_request", "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "selected_item_id": null, "result_count": null, "fit_card": null, "total_ms": 0.1, "queue_wait_ms": null, "run_ms": null, "stage_ms": {}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T00:09:01.107+00:00", "request_id": "915043b1fb17", "run_label": "m3-failures", "route": "/ask", "query": "", "status": 400, "outcome": "bad_request", "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "selected_item_id": null, "result_count": null, "fit_card": null, "total_ms": 0.0, "queue_wait_ms": null, "run_ms": null, "stage_ms": {}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T00:09:01.166+00:00", "request_id": "6ee2ccdd54bc", "run_label": "m3-nomatch", "route": "/ask", "query": "designer ballgown size XXS under $5", "status": 200, "outcome": "no_results", "error": "No listings matched after FitFindr dropped the size filter for XXS. Try broader keywords or a higher price limit.", "selected_item_id": null, "result_count": 0, "fit_card": null, "total_ms": 522.6, "queue_wait_ms": 0.0, "run_ms": 522.3, "stage_ms": {"parse": 0.0, "search": 295.6, "search_retry": 226.7}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
{"timestamp": "2026-11-15T00:09:01.690+00:00", "request_id": "1d32a80dace5", "run_label": "m3-nomatch", "route": "/ask", "query": "wool sweater under $40", "status": 200, "outcome": "no_results", "error": "No listings matched. Try broader keywords, a different size, or a higher price limit.", "selected_item_id": null, "result_count": 0, "fit_card": null, "total_ms": 252.2, "queue_wait_ms": 0.0, "run_ms": 252.1, "stage_ms": {"parse": 0.0, "search": 252.0}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "rate_limit_wait_s": 0.0, "model": "gemini-3.5-flash-lite", "cache_enabled": false}
```

**A failed run, and one that left no record.** My first cost run sent the same
ten queries back to back with no delay (`--label m3-cost`, report in
`results/drive_m3-cost.md`). Eight returned fit cards. Requests 8 and 9 came
back to the caller as `500` after almost exactly 30 seconds, and **neither has
a line in the log**:

```
| 8 | {"query": "floral dress under $35"} | 500 | 30047.3 | - | non-JSON error body |
| 9 | {"query": "leather bag"}            | 500 | 30261.5 | - | non-JSON error body |
```

gunicorn's own output from that run shows why:

```
  [rate limit] 15 requests used this minute. Waiting 46s. This is normal.
[2026-11-14 19:08:00 -0500] [60205] [CRITICAL] WORKER TIMEOUT (pid:60207)
  [rate limit] service pushed back. Waiting 58s (attempt 1 of 5). This is the limiter doing its job, not a bug.
[2026-11-14 19:08:31 -0500] [60205] [CRITICAL] WORKER TIMEOUT (pid:60632)
  [rate limit] 15 requests used this minute. Waiting 4s. This is normal.
```

Request 8 was the 15th model call in a minute, so `generate.py::_wait_for_slot`
slept 46 seconds. gunicorn's default worker timeout is 30 seconds, so it killed
the worker during the sleep, before `serve.py` could write the record. The
replacement worker started with an empty rate-limit window, sent request 9's
call straight away, got a 429 from Gemini, and was killed again during a
58-second backoff. The log I built records every failure the service handles,
but not one that kills the process running it. These two absences are visible
only because `drive.py` compares what the caller saw with what the log holds.

**What It Costs**

Measured, not taken from a pricing page. I ran the five matching queries twice
each against the running service, with the cache off and a six-second pause
between requests so the rate limiter didn't distort the timing (`--label
m3-cost-paced`, report in `results/drive_m3-cost-paced.md`). Each of the ten
records carries the tokens Gemini reported on `usage_metadata` for that
request's two model calls.

| Measure (10 fit-card runs) | Mean | Min | Max |
|---|---|---|---|
| Model calls per run | 2 | 2 | 2 |
| Prompt tokens per run | 824.3 | 759 | 875 |
| Output tokens per run | 217.7 | 164 | 271 |
| Total tokens per run | 1042 | 923 | 1146 |
| Service time per run (`total_ms`) | 2342 ms | 1773 ms | 5454 ms |

An empty search costs nothing: zero model calls and about 0.25 to 0.5 seconds
of MCP search. A rejected body costs nothing and takes under a millisecond.

Actual spend: $0. The key is on Gemini's free tier, so the real limit is the
quota, not money. One fit-card run uses 2 of the 15 requests a minute the free
tier allows.

A hundred people a day, one fit-card query each: 100 × 1042 = 104,200 tokens a
day (82,430 prompt + 21,770 output), and 100 × 2 = 200 model calls a day. At 15
calls a minute that is about 13 minutes of the free tier's per-minute allowance
if they all arrived at once; spread across a day it never comes near the
limit. The dollar figure for paid use goes in Milestone 7.

**Run Log and Verdicts**

Three trials of every criterion in `criteria.md`, with nothing in the service
changed between them. Each trial is one run of `./run_trial.sh N`, which starts
the service with the RUNNING.md command, runs the C1/C4 burst, stops the
service and idles 65 s so Gemini's per-minute window is clear, starts it again
for the C2 warm-up, the C2/C3 paced run and the two C5 sets, then scores the
trial with `score.py N`. `score.py` only applies the thresholds written in
`criteria.md`; it reads the caller's rows from `results/drive_<label>.json` and
the service's records from `logs/requests.jsonl`. Each trial was separated
from the last by at least 65 s of idle.

| Criterion | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|
| C1. Every burst request has a log record (10 of 10) | 10/10 | 9/10 | 9/10 | MISSED |
| C2. At least 9 of 10 paced requests at or under 2500 ms | 8/10 | 9/10 | 7/10 | MISSED |
| C3. All 10 paced runs are fit cards, 2 calls, at most 1300 tokens | 10/10 | 10/10 | 10/10 | MET |
| C4. All 10 burst requests get a 200 within 65 s, never a bare 500 | 10/10 | 9/10 | 9/10 | MISSED |
| C5. 4/4 bad bodies get 400, 2/2 impossible queries get no_results, 0 calls | 6/6 | 6/6 | 6/6 | MET |

A criterion is MET only when all three runs pass, because each one says "in
each of 3 trials". The full output of every trial is in
`results/trial_tN_console.txt`, the scores in `results/score_tN.txt`, the
per-label reports in `results/drive_<label>.md`, and gunicorn's stderr in
`results/server_tN_burst.log` and `results/server_tN_paced.log`.

*C1, run 2.* The driver's `summarise()` in `drive.py` compares the request ids
the caller received with the records `serve.py`'s `_finish()` wrote:

```
- requests sent: 10
- status counts: 200: 9, 500: 1
- requests with a log record: 9 of 10
```

Run 1 read 10 of 10 and run 3 read 9 of 10. Run 1 passed by luck, not because
anything was different: Gemini was slow during that run (3 to 9 s per call, see
C2), so the ten requests took about two minutes and never reached 15 model
calls in one minute.

*C4, runs 2 and 3.* `score.py`'s `c4()` on the caller's rows:

```
Trial 2  C4 FAIL  9 of 10 returned 200 with fit_card or model_error within 65 s;
                  failing: ["#8 status=500 client_ms=30953.4 error='non-JSON error body'"]
Trial 3  C4 FAIL  9 of 10 returned 200 with fit_card or model_error within 65 s;
                  failing: ["#7 status=500 client_ms=30053.5 error='non-JSON error body'"]
```

The failing row from `results/drive_c1-burst-t3.json` has no `request_id`,
which is why C1 failed in the same run:

```
{'body': {'query': 'denim jacket under $60'}, 'status': 500, 'client_ms': 30053.5,
 'request_id': None, 'outcome': 'non-JSON error body', 'client_error': None}
```

gunicorn's stderr for run 2 (`results/server_t2_burst.log`) shows where it
happened. The traceback ends in `generate.py`'s `_wait_for_slot()` sleeping:

```
  [rate limit] 15 requests used this minute. Waiting 46s. This is normal.
[2026-11-15 00:31:10 -0500] [92375] [CRITICAL] WORKER TIMEOUT (pid:92379)
  File ".../serve.py", line 187, in ask
    session = run_agent(query, wardrobe)
  File ".../agent.py", line 294, in run_agent
    session["fit_card"] = _timed(
  File ".../tools.py", line 299, in create_fit_card
    response = generate(prompt).strip()
  File ".../generate.py", line 326, in generate
    _wait_for_slot()
  File ".../generate.py", line 123, in _wait_for_slot
    time.sleep(sleep_for)
  File ".../gunicorn/workers/base.py", line 204, in handle_abort
    sys.exit(1)
SystemExit: 1
```

Run 3 reached the same place by a different route: Gemini itself answered with
a 429 before the local limiter filled, and the retry loop in `generate()` slept
for the 46 s it asked for (`results/server_t3_burst.log`):

```
  [rate limit] service pushed back. Waiting 46s (attempt 1 of 5). This is the limiter doing its job, not a bug.
[2026-11-15 00:35:44 -0500] [94388] [CRITICAL] WORKER TIMEOUT (pid:94392)
SystemExit: 1
```

*C2, all runs.* `score.py`'s `c2()` reads `total_ms` from each record:

```
Trial 1  C2 FAIL  8 of 10 records with total_ms <= 2500; total_ms = [9926.6, 2021.6, 1693.0, 2157.0, 2447.0, 1881.1, 2025.4, 1987.3, 5150.0, 2151.2]
Trial 2  C2 PASS  9 of 10 records with total_ms <= 2500; total_ms = [1849.5, 2371.8, 1716.7, 2220.7, 1942.9, 2059.6, 11673.7, 2226.5, 1973.6, 2108.1]
Trial 3  C2 FAIL  7 of 10 records with total_ms <= 2500; total_ms = [1952.8, 2312.8, 1718.3, 1952.5, 2146.0, 2685.2, 9701.5, 2648.1, 2266.1, 1973.0]
```

The slowest record in run 3, written by `serve.py`'s `ask()` with the stage
times from `agent.py`'s `_timed()`, shows the time went to the rate limiter,
not the agent:

```json
{"request_id": "2f84d3e6af8b", "run_label": "c2-paced-t3", "status": 200, "outcome": "fit_card", "total_ms": 9701.5, "rate_limit_wait_s": 7.78, "stage_ms": {"parse": 0.0, "search": 262.0, "compare_price": 214.9, "suggest_outfit": 777.9, "create_fit_card": 8445.9}, "model_calls": 2, "prompt_tokens": 813, "output_tokens": 225}
```

The other run 3 misses (2685 and 2648 ms) had no limiter wait and are slow
model calls. In run 1 the two misses were a slow first call (`suggest_outfit`
took 8368 ms with no limiter wait) and a 3.05 s limiter wait.

*C3, all runs.* `score.py`'s `c3()`:

```
Trial 1  C3 PASS  10 of 10 records are fit_card with 2 calls and <= 1300 tokens
Trial 2  C3 PASS  10 of 10 ...
Trial 3  C3 PASS  10 of 10 ...
```

Across the 30 records tokens ranged from 923 to 1164 and `model_calls` was 2
every time; the per-record values are in `results/score_tN.txt`.

*C5, all runs.* `score.py`'s `c5()`, and one record of each kind from run 2,
written by `serve.py`'s `ask()` (the 400 path returns before the lock; the
no-match path returns from `agent.py`'s `run_agent()` after the size retry):

```
Trial 1  C5 PASS  4 of 4 bad bodies got 400 bad_request; 2 of 2 impossible queries got no_results; model calls across all 6: 0
Trial 2  C5 PASS  (same)
Trial 3  C5 PASS  (same)
```

```json
{"request_id": "331f936f212c", "run_label": "c5-bad-t2", "status": 400, "outcome": "bad_request", "total_ms": 0.0, "rate_limit_wait_s": 0.0, "stage_ms": {}, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0}
{"request_id": "b31275d65f0a", "run_label": "c5-nomatch-t2", "status": 200, "outcome": "no_results", "total_ms": 440.2, "rate_limit_wait_s": 0.0, "stage_ms": {"parse": 0.0, "search": 221.6, "search_retry": 218.3}, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0}
```

**The Improvement**

*Diagnosis of each missed criterion (from the M5 runs above).*

- **C1 and C4, one cause.** Stage: the second model call, inside
  `generate.py`. When a burst passes 15 calls in a minute, `generate()` sleeps
  before the next call. In run 2 that was `_wait_for_slot()` (local limiter,
  46 s); in run 3 it was the retry loop after Gemini returned a 429 (46 s, the
  delay Gemini asked for). gunicorn's default worker timeout is 30 s, so the
  arbiter aborts the worker mid-sleep with `SystemExit` (the `handle_abort`
  frame in `results/server_t2_burst.log`). `SystemExit` is a `BaseException`,
  so the `except Exception` in `serve.py`'s `ask()` never sees it and
  `_finish()` never runs: no log record (C1) and gunicorn's own HTML 500 page
  for the caller (C4). Run 1 passed only because Gemini was slow enough that
  run that the burst never reached 15 calls a minute.
- **C2.** Stage: also `create_fit_card`'s model call. Two causes, both outside
  the service code. The warm-up's 2 calls plus 20 paced calls at about 8 s
  spacing exceed 15 calls in a 60 s window, so one request per run waits
  3 to 9 s in `_wait_for_slot()` (`rate_limit_wait_s` 7.78 in the run 3
  record above). The rest are single Gemini calls that take 2.5 to 8 s with no
  limiter wait. I did not try to fix C2: the first cause is the free-tier
  quota meeting my own test's pacing, and the second is the provider.

*What I changed.* One new file, `gunicorn.conf.py`, which gunicorn loads from
the working directory on its own, so the start command in RUNNING.md and in
`criteria.md` is unchanged:

```python
timeout = 90
```

90 s covers the longest sleep `generate.py` can do inside one request (65 s,
the cap in `_retry_delay()`; `_wait_for_slot()` waits at most about 60 s) plus
one agent run. `gunicorn --print-config serve:app` now reports
`timeout = 90`. No agent, tool or logging code changed. RUNNING.md has a note
that the service must be started from the repo root so the file is found.

*Re-run.* Three more full trials with the same script and the same 65 s idle
between them, labelled t4 to t6 so the before files are untouched
(`./run_trial.sh 4`, `5`, `6`; scores in `results/score_t4.txt` to
`score_t6.txt`).

| Criterion | Before: Run 1 | Run 2 | Run 3 | Verdict | After: Run 4 | Run 5 | Run 6 | Verdict |
|---|---|---|---|---|---|---|---|---|
| C1. Log record per burst request | 10/10 | 9/10 | 9/10 | MISSED | 10/10 | 10/10 | 10/10 | MET |
| C2. At least 9 of 10 paced at or under 2500 ms | 8/10 | 9/10 | 7/10 | MISSED | 8/10 | 5/10 | 8/10 | MISSED |
| C3. Fit card, 2 calls, at most 1300 tokens | 10/10 | 10/10 | 10/10 | MET | 10/10 | 10/10 | 9/10 | MISSED |
| C4. 200 within 65 s, never a bare 500 | 10/10 | 9/10 | 9/10 | MISSED | 10/10 | 10/10 | 10/10 | MET |
| C5. Bad input and no-match, 0 calls | 6/6 | 6/6 | 6/6 | MET | 6/6 | 6/6 | 6/6 | MET |

*Did it help, and how do I know.* Yes for C1 and C4, and the after runs
exercised the failure rather than avoiding it. In every after trial the
eighth burst request hit the limiter for about 44 s, longer than the old 30 s
timeout, and still came back. The server logs show the sleep and no
`WORKER TIMEOUT` (`results/server_t4_burst.log`, same in t5 and t6):

```
  [rate limit] 15 requests used this minute. Waiting 44s. This is normal.
```

and the record `serve.py` wrote for that request in run 4:

```json
{"request_id": "81039153aee1", "run_label": "c1-burst-t4", "status": 200, "outcome": "fit_card", "total_ms": 46124.2, "rate_limit_wait_s": 44.06, "stage_ms": {"parse": 0.0, "search": 245.2, "suggest_outfit": 718.4, "create_fit_card": 45160.1}}
```

(runs 5 and 6: 46359.9 ms with 43.97 s waited, and 46224.5 ms with 44.29 s
waited, both `fit_card`). The caller waited about 46 s for a fit card instead
of getting an HTML 500 at 30 s, inside C4's 65 s limit.

C2 stayed missed, as expected, since nothing changed on its path. Run 5's
5 of 10 had one 6.39 s limiter wait; the other four misses were 2.6 to 3.2 s
with no wait, so Gemini was slower in that run.

C3 went from MET to MISSED in run 6, and not because of the change. One paced
request (`59dd4cbfa215`, "flannel shirt under $25") returned
`outcome: "model_error"` after 1.25 s in `suggest_outfit` with
`model_calls: 1` and no rate-limit wait. That is `generate()` raising
`ModelUnavailable` for a non-429 provider error, which a 90 s worker timeout
cannot cause or prevent. The record cannot say which error it was, because
`agent.py`'s `ModelUnavailable` handler replaces the provider's message with
a generic one, and the gunicorn log shows nothing for it. That gap is listed
under What's Still Broken. The service handled it the way C4 asks for (a
200 with a clear error), but C3 requires every paced run to be a fit card, so
it counts as a miss.
