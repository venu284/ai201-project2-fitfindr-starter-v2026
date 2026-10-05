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
maximum price, and searches a local listings dataset. If nothing matches, it
stops and tells the user to broaden the keywords, try another size, or raise the
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

**Branch rules:** If `search_listings` returns an empty list, store a message in `session["error"]` telling the user to try broader keywords, a different size, or a higher price limit, then stop. Otherwise, store the first result in `session["selected_item"]`. If exactly one listing matched, skip `compare_price` and record why. If several listings matched, call `compare_price` with the selected item. Both matching paths then call `suggest_outfit` and `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** `agent.py::run_agent` uses regular expressions. It recognizes `size <value>` as the size and `under`, `below`, or `less than` followed by a dollar amount as the maximum price. It removes those parts from the query and uses the remaining text as the description.

**What moves through the session:** The session stores the original `query`, then the parsed `description`, `size`, and `max_price`. `search_listings` stores its results in `search_results`. The first result moves to `selected_item`. The match-count branch stores either the fourth tool's return value or the skip reason in `price_comparison`. The selected item then passes to `suggest_outfit` with the saved `wardrobe`. The returned string moves to `outfit_suggestion`, then `outfit_suggestion` and `selected_item` pass to `create_fit_card`, whose result is stored in `fit_card`.

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
Remembered 2 wardrobe items in /Users/venu/Documents/AI201/ai201-project2-fitfindr-starter-v2026/.fitfindr/wardrobe.json.

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
- *What I changed:* I added a regression check and normalized sentence-ending
  punctuation in the outfit before constructing the two-sentence fallback.

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
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

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
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



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
