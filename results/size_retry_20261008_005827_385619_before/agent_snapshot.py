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
from tools import suggest_outfit, create_fit_card
from mcp_client import call_tool
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

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
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "price_comparison": None,    # comparison returned by the fourth tool
        "wardrobe": wardrobe,        # the user's wardrobe
        "styling_mode": None,        # chosen by the wardrobe branch
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
    Implemented workflow, following the branch rule from Milestone 2.
    An additional compare stage saves compare_prices(selected_item) in
    session["price_comparison"] before outfit generation.
    The choose_styling stage selects general advice for an empty wardrobe
    or combinations using existing wardrobe items.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings through MCP with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    trace.start_trace()
    session = new_session(query, wardrobe)
    stage = "parse"
    iterations = 0

    try:
        while True:
            iterations += 1
            trace.check_iterations(iterations)
    
            if stage == "parse":
                description = session["query"]
    
                price_match = re.search(
                    r"\b(?:under|below|up to)\s*\$?\s*(\d+(?:\.\d{1,2})?)",
                    description,
                    flags=re.IGNORECASE,
                )
                max_price = None
                if price_match:
                    max_price = float(price_match.group(1))
                    description = (
                        description[:price_match.start()]
                        + " "
                        + description[price_match.end():]
                    )
    
                size_match = re.search(
                    r"\b(?:in\s+)?size\s+"
                    r"(W\d+\s+L\d+|US\s+\d+(?:\.\d+)?|"
                    r"[A-Za-z0-9]+(?:/[A-Za-z0-9]+)?)\b",
                    description,
                    flags=re.IGNORECASE,
                )
                size = None
                if size_match:
                    size = size_match.group(1).strip()
                    description = (
                        description[:size_match.start()]
                        + " "
                        + description[size_match.end():]
                    )
    
                description = re.sub(
                    r"^\s*(?:looking for|find me|find|a|an)\b\s*",
                    "",
                    description,
                    flags=re.IGNORECASE,
                )
                description = re.sub(
                    r"^\s*(?:a|an)\b\s*",
                    "",
                    description,
                    flags=re.IGNORECASE,
                )
                description = " ".join(
                    description.replace(",", " ").split()
                )
    
                session["parsed"] = {
                    "description": description,
                    "size": size,
                    "max_price": max_price,
                }
                trace.step("parse_query", inputs=query, returned=repr(session["parsed"]))
                stage = "search"
    
            elif stage == "search":
                session["search_results"] = call_tool(
                    "search_listings", session["parsed"]
                )
    
                trace.step("search_listings (via MCP)",
                           inputs=repr(session["parsed"]),
                           returned=session["search_results"])
    
                if not session["search_results"]:
                    session["error"] = (
                        "No matching listings were found. Try different "
                        "description keywords, another size, or a higher budget."
                    )
                    trace.step("empty_search", note=session["error"])
                    return session
    
                session["selected_item"] = session["search_results"][0]
                trace.step("select_item", returned=session["selected_item"])
                stage = "compare"
    
            elif stage == "compare":
                session["price_comparison"] = call_tool(
                    "compare_prices", {"new_item": session["selected_item"]}
                )
                trace.step("compare_prices (via MCP)", inputs=session["selected_item"],
                           returned=repr(session["price_comparison"]))
                stage = "choose_styling"
    
            elif stage == "choose_styling":
                if session["wardrobe"].get("items"):
                    session["styling_mode"] = "wardrobe_combinations"
                    stage = "outfit"
                else:
                    session["styling_mode"] = "general_advice"
                    stage = "general_advice"
    
                trace.step("choose_styling",
                           inputs=f"wardrobe items: {len(session['wardrobe'].get('items', []))}",
                           returned=session["styling_mode"],
                           note=f"Next stage: {stage}")
    
            elif stage == "general_advice":
                session["outfit_suggestion"] = suggest_outfit(
                    session["selected_item"],
                    session["wardrobe"],
                )
                trace.step("suggest_outfit",
                           inputs=f"item={session['selected_item']['id']}; wardrobe IDs="
                                  + repr([item.get('id') for item in session['wardrobe'].get('items', [])]),
                           returned=session["outfit_suggestion"],
                           note=f"Styling mode: {session['styling_mode']}")
    
                if not session["outfit_suggestion"].strip():
                    session["error"] = (
                        "No general styling advice was generated. Please try again."
                    )
                    return session
    
                stage = "caption"
    
            elif stage == "outfit":
                session["outfit_suggestion"] = suggest_outfit(
                    session["selected_item"],
                    session["wardrobe"],
                )
                trace.step("suggest_outfit",
                           inputs=f"item={session['selected_item']['id']}; wardrobe IDs="
                                  + repr([item.get('id') for item in session['wardrobe'].get('items', [])]),
                           returned=session["outfit_suggestion"],
                           note=f"Styling mode: {session['styling_mode']}")
    
                if not session["outfit_suggestion"].strip():
                    session["error"] = (
                        "No outfit suggestion was generated. Please try again."
                    )
                    return session
    
                stage = "caption"
    
            elif stage == "caption":
                session["fit_card"] = create_fit_card(
                    session["outfit_suggestion"],
                    session["selected_item"],
                )
                trace.step("create_fit_card",
                           inputs=f"item={session['selected_item']['id']}; outfit="
                                  + session['outfit_suggestion'],
                           returned=session["fit_card"])
    
                if not session["fit_card"].strip():
                    session["error"] = (
                        "No caption was generated. Please try again."
                    )
    
                return session
    except ModelUnavailable:
        failed_tool = "create_fit_card" if stage == "caption" else "suggest_outfit"
        session["error"] = (
            f"The model call for {failed_tool} failed. Check your internet "
            "connection and GEMINI_API_KEY in .env, run python test.py, "
            "then try again."
        )
        trace.step(failed_tool + " (failed)",
                   note=session["error"])
        return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  price comparison: {session['price_comparison']}")
    print(f"  styling mode: {session['styling_mode']}")
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
