"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re

import config
import trace
from mcp_client import call_tool
from tools import create_fit_card, suggest_outfit
from generate import ModelUnavailable


SIZE_PATTERN = re.compile(r"\bsize\s+([\w/-]+)", re.IGNORECASE)
PRICE_PATTERN = re.compile(
    r"\b(?:under|below|less than)\s*\$?(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)


# ── session state ─────────────────────────────────────────────────────────────

def parse_query(query: str) -> dict:
    size_match = SIZE_PATTERN.search(query)
    price_match = PRICE_PATTERN.search(query)
    description = SIZE_PATTERN.sub("", query)
    description = PRICE_PATTERN.sub("", description).strip(" ,")

    return {
        "description": description,
        "size": size_match.group(1) if size_match else None,
        "max_price": float(price_match.group(1)) if price_match else None,
    }


def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "search_relaxation": None,   # why a sized search was retried without size
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "price_comparison": None,    # compare_price result, or why it was skipped
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    IMPLEMENTED FLOW — this follows the branch rule from Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - when the query included a size, retry once without that filter
              - put a message in session["error"] saying what the user could
                change if the retry also finds nothing
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. If one listing matched, record why price comparison was skipped. If
         several matched, call compare_price() with the selected item. Put the
         result in session["price_comparison"].

      7. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      8. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      9. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    session = new_session(query, wardrobe)
    iterations = 0

    while True:
        iterations += 1
        trace.check_iterations(iterations)

        session["parsed"] = parse_query(query)
        description = session["parsed"]["description"]
        search_inputs = (
            f"description={description!r}, size={session['parsed']['size']!r}, "
            f"max_price={session['parsed']['max_price']!r}"
        )
        trace.step("parse_query", inputs=query, returned=search_inputs)

        session["search_results"] = call_tool("search_listings", session["parsed"])
        trace.step(
            "search_listings (via MCP)",
            inputs=search_inputs,
            returned=session["search_results"],
        )
        if not session["search_results"]:
            original_size = session["parsed"]["size"]
            if original_size is None:
                session["error"] = (
                    "No listings matched. Try broader keywords, a different size, "
                    "or a higher price limit."
                )
                trace.step(
                    "search_results branch",
                    inputs="0 matches",
                    returned=session["error"],
                    note="stop",
                )
                return session

            relaxed_search = {**session["parsed"], "size": None}
            session["search_relaxation"] = (
                f"No listings matched size {original_size}, so FitFindr "
                "retried without the size filter."
            )
            relaxed_inputs = (
                f"description={description!r}, size=None, "
                f"max_price={session['parsed']['max_price']!r}"
            )
            session["search_results"] = call_tool(
                "search_listings", relaxed_search
            )
            trace.step(
                "search_listings retry (via MCP)",
                inputs=relaxed_inputs,
                returned=session["search_results"],
                note="dropped size filter",
            )
            trace.step(
                "search relaxation",
                returned=session["search_relaxation"],
            )

            if not session["search_results"]:
                session["error"] = (
                    "No listings matched after FitFindr dropped the size filter "
                    f"for {original_size}. Try broader keywords or a "
                    "higher price limit."
                )
                trace.step(
                    "search_results branch",
                    inputs="0 matches after retry",
                    returned=session["error"],
                    note="stop",
                )
                return session

        session["selected_item"] = session["search_results"][0]
        trace.step(
            "select_item",
            inputs=f"first of {len(session['search_results'])} matches",
            returned=f"id={session['selected_item']['id']}, title={session['selected_item']['title']}",
        )
        if len(session["search_results"]) == 1:
            session["price_comparison"] = {
                "status": "skipped_single_match",
                "category": session["selected_item"].get("category"),
                "item_price": session["selected_item"].get("price"),
                "median_price": None,
                "difference": None,
                "comparable_count": 0,
                "message": (
                    "Only one listing matched, so FitFindr skipped price comparison."
                ),
            }
            trace.step(
                "compare_price (skipped)",
                inputs="1 match",
                returned=session["price_comparison"]["message"],
            )
        else:
            session["price_comparison"] = call_tool(
                "compare_price", {"new_item": session["selected_item"]}
            )
            trace.step(
                "compare_price (via MCP)",
                inputs=session["selected_item"],
                returned=session["price_comparison"]["message"],
            )

        wardrobe_items = session["wardrobe"].get("items") or []
        first_wardrobe_item = wardrobe_items[0].get("name") if wardrobe_items else None
        outfit_inputs = (
            f"new_item_id={session['selected_item']['id']}, "
            f"wardrobe_items={len(wardrobe_items)}, first_item={first_wardrobe_item!r}"
        )
        try:
            session["outfit_suggestion"] = suggest_outfit(
                session["selected_item"], session["wardrobe"]
            )
        except ModelUnavailable:
            session["error"] = (
                "The model couldn't be reached while suggesting an outfit. "
                "Check GEMINI_API_KEY and your internet connection, then try again."
            )
            trace.step("suggest_outfit", inputs=outfit_inputs, returned=session["error"])
            return session
        trace.step(
            "suggest_outfit", inputs=outfit_inputs, returned=session["outfit_suggestion"]
        )

        fit_inputs = (
            f"new_item_id={session['selected_item']['id']}, "
            f"outfit={session['outfit_suggestion']}"
        )
        try:
            session["fit_card"] = create_fit_card(
                session["outfit_suggestion"], session["selected_item"]
            )
        except ModelUnavailable:
            session["error"] = (
                "The model couldn't be reached while creating the fit card. "
                "Check GEMINI_API_KEY and your internet connection, then try again."
            )
            trace.step("create_fit_card", inputs=fit_inputs, returned=session["error"])
            return session
        trace.step("create_fit_card", inputs=fit_inputs, returned=session["fit_card"])
        return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    if session.get("search_relaxation"):
        print(f"  {session['search_relaxation']}")
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    comparison = session.get("price_comparison") or {}
    if comparison.get("message"):
        print(f"  price:    {comparison['message']}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
