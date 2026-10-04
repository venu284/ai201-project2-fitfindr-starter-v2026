"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    requested_tokens = set(re.findall(r"[a-z0-9]+", description.casefold()))
    normalized_size = " ".join(size.casefold().split()) if size is not None else None
    alpha_size = bool(normalized_size and re.fullmatch(r"[a-z]+", normalized_size))
    scored_listings = []

    for listing in load_listings():
        if max_price is not None and listing["price"] > max_price:
            continue

        if normalized_size is not None:
            listing_size = " ".join(listing["size"].casefold().split())
            if alpha_size:
                listing_size_tokens = re.findall(r"[a-z]+", listing_size)
                if normalized_size not in listing_size_tokens:
                    continue
            elif normalized_size != listing_size:
                continue

        searchable_values = [
            listing["title"],
            listing["description"],
            listing["category"],
            *listing["style_tags"],
            *listing["colors"],
        ]
        if listing["brand"] is not None:
            searchable_values.append(listing["brand"])

        searchable_tokens = set(
            re.findall(r"[a-z0-9]+", " ".join(searchable_values).casefold())
        )
        score = len(requested_tokens & searchable_tokens)
        if score:
            scored_listings.append((score, listing))

    scored_listings.sort(key=lambda scored: scored[0], reverse=True)
    return [
        listing
        for _, listing in scored_listings[:config.SEARCH_RESULT_LIMIT]
    ]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    wardrobe_items = wardrobe.get("items") or []

    colors = ", ".join(new_item.get("colors") or []) or "Not listed"
    style_tags = ", ".join(new_item.get("style_tags") or []) or "Not listed"
    price = new_item.get("price")
    formatted_price = (
        f"${price:.2f}" if isinstance(price, (int, float)) else "Not listed"
    )
    item_details = "\n".join(
        [
            f"Title: {new_item.get('title') or 'Untitled item'}",
            f"Description: {new_item.get('description') or 'Not listed'}",
            f"Category: {new_item.get('category') or 'Not listed'}",
            f"Size: {new_item.get('size') or 'Not listed'}",
            f"Condition: {new_item.get('condition') or 'Not listed'}",
            f"Price: {formatted_price}",
            f"Colors: {colors}",
            f"Style tags: {style_tags}",
            f"Brand: {new_item.get('brand') or 'Not listed'}",
            f"Platform: {new_item.get('platform') or 'Not listed'}",
        ]
    )

    if wardrobe_items:
        formatted_wardrobe = []
        for index, item in enumerate(wardrobe_items, start=1):
            item_colors = ", ".join(item.get("colors") or []) or "Not listed"
            item_tags = ", ".join(item.get("style_tags") or []) or "Not listed"
            formatted_wardrobe.append(
                "\n".join(
                    [
                        f"Wardrobe item {index}:",
                        f"Name: {item.get('name') or 'Unnamed item'}",
                        f"Category: {item.get('category') or 'Not listed'}",
                        f"Colors: {item_colors}",
                        f"Style tags: {item_tags}",
                        f"Notes: {item.get('notes') or 'None'}",
                    ]
                )
            )

        wardrobe_details = "\n\n".join(formatted_wardrobe)
        prompt = (
            "Suggest 1-2 outfit ideas for the listing below using pieces from "
            "the saved wardrobe. Use the exact saved item names in each idea, "
            "and do not invent wardrobe pieces.\n\n"
            f"Listing:\n{item_details}\n\n"
            f"Saved wardrobe:\n{wardrobe_details}"
        )
    else:
        prompt = (
            "Give general styling advice for the listing below. Suggest types "
            "of clothing, shoes, or accessories that could work with it. Do not "
            "claim that the user owns any suggested pieces.\n\n"
            f"Listing:\n{item_details}"
        )

    response = generate(prompt).strip()
    if response:
        return response

    return (
        "For a flexible outfit, style this item with simple neutral basics, "
        "balance its proportions, and choose shoes and accessories that echo "
        "one of its colors."
    )


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    cleaned_outfit = outfit.strip()
    if not cleaned_outfit:
        return "I couldn't create a fit card because the outfit suggestion was empty."

    title = new_item["title"]
    price = f"${new_item['price']:.2f}"
    platform = new_item["platform"]
    colors = ", ".join(new_item.get("colors") or []) or "Not listed"
    style_tags = ", ".join(new_item.get("style_tags") or []) or "Not listed"

    prompt = (
        "Write a social-media fit card caption in 2-4 sentences (two to four "
        "sentences). In the caption, mention the item, its exact price, and its "
        "platform exactly once each. Describe the outfit's specific vibe rather "
        "than writing a generic product description.\n\n"
        f"Title: {title}\n"
        f"Description: {new_item.get('description') or 'Not listed'}\n"
        f"Category: {new_item.get('category') or 'Not listed'}\n"
        f"Condition: {new_item.get('condition') or 'Not listed'}\n"
        f"Colors: {colors}\n"
        f"Style tags: {style_tags}\n"
        f"Price: {price}\n"
        f"Platform: {platform}\n"
        f"Outfit: {cleaned_outfit}"
    )

    response = generate(prompt).strip()
    if response:
        return response

    fallback_outfit = re.sub(r"[.!?]+(?=\s|$)", ";", cleaned_outfit)
    fallback_outfit = re.sub(r"\s*;\s*", "; ", fallback_outfit).strip(" ;")
    return (
        f"{title} is a {price} find from {platform}. "
        f"Wear it with {fallback_outfit} for an easy, put-together look."
    )
