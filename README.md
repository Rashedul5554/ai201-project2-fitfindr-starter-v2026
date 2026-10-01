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
> The three required tools have individual development runs recorded below.
> The planning loop and bonus features still need implementation and verification.
>
> **The rest of this file is your submission.** Fill it in as you go.

### Milestone 1 — Setup and data exploration

The environment check passed all 10 checks. I inspected six listings and the wardrobe fields. Listings include title, description, size, price, and style_tags. Prices are numbers, style_tags are lists, and sizes include formats such as S/M and XL (oversized).

I ran the query 'vintage graphic tee under $30'. The starter reported that the planning loop is not built yet, which is the expected starting behavior.

## Planned Unit 3 Stretch Features

These features are declared before implementation.

- **Fourth tool — compare_prices:** Takes the selected listing and compares its price with other listings in the same category. Returns a dictionary containing the number of comparison items, their median price, and the selected item's difference from that median. If no comparison items exist, returns a count of zero and None for the median and difference. The agent will call this tool after selecting an item. Comparisons describe this dataset, not market value.

- **Second planning-loop branch — empty wardrobe:** If the wardrobe has no items, the loop will request general styling advice. Otherwise, it will request combinations using the user's stored wardrobe. I will record runs showing both paths.

- **Style memory:** Save user-provided wardrobe items locally between runs. I will demonstrate one run that stores a wardrobe change and a separate run that loads and uses that change.

After implementation, I will add actual run output and explain what each feature changed.

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

FitFindr is being built to accept clothing requests such as "a vintage graphic tee under $30, size M," search a local mock listings dataset, suggest outfits, and write a short caption. The three required tools have been implemented and exercised individually. The full agent workflow and planned bonus features are not yet demonstrated; their output will be added after implementation.



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

- **What it does:** Searches the listings data for items matching the requested description, size, and maximum price.
- **Inputs:** description (str), size (str or None, meaning no size filter), and max_price (float or None, meaning no price limit).
- **Returns:** A list of matching listing dictionaries, preserving each listing’s id, title, description, category, style_tags, size, condition, price, colors, brand, and platform.
- **When it has nothing:** Returns an empty list [] when no listings match.

**Search matching rules:** Match whole keywords against the listing's title, description, and style_tags, ignoring capitalization. Count each matching query keyword once. Exclude listings with zero matches and sort by highest match count, keeping the original data order for ties. Return at most config.SEARCH_RESULT_LIMIT listings. When max_price is provided, include only prices less than or equal to it.

**Size matching rules:** Ignore capitalization and parenthetical fit notes. Match complete size labels or slash-separated alternatives: M matches S/M, and XL matches XL (oversized). L does not match XL, and S does not match US 9. When size is None, skip size filtering.

### `suggest_outfit`

- **What it does:** Uses the model to suggest one or two outfits combining the selected item with pieces from the user's wardrobe.
- **Inputs:** new_item (dict containing a listing) and wardrobe (dict with an items key containing a list of wardrobe items).
- **Returns:** A non-empty string with one or two outfit suggestions naming existing wardrobe pieces when available, or general styling advice when the wardrobe is empty.
- **When it has nothing:** If the wardrobe's items list is empty, returns general styling advice for the selected item.

### `create_fit_card`

- **What it does:** Uses the model to write a short social caption about the selected item and outfit.
- **Inputs:** outfit (str containing outfit suggestions) and new_item (dict containing the selected listing).
- **Returns:** A two-to-four-sentence caption mentioning the item, its price, and its platform once each, with a specific description of the style.
- **When it has nothing:** If outfit is empty or contains only whitespace, returns "Cannot create a fit card because no outfit suggestion was provided."

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

**Planned branch rule (not yet verified in the agent):** If search_listings returns an empty list, save a message in the session suggesting that the user change the description, size, or budget, then stop without calling suggest_outfit or create_fit_card. Otherwise, save the first matching listing in the session as selected_item, pass that saved item to suggest_outfit, save the outfit suggestion, and use the saved suggestion and item to call create_fit_card. Save the resulting fit card in the session.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Pending implementation review of agent.py.

**What moves through the session:** Planned: search results, selected item, outfit suggestion, and fit card. Exact session fields and actual behavior will be documented when the loop is implemented.

---

## Sample Run

These are actual development runs copied from my terminal. They are individual tool checks, not the Unit 4 acceptance evaluation.

### One full agent query

Pending: connect the tools in `agent.py`, then record a complete query and its actual output.

### search_listings — keyword and price filtering

```text
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair','price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}]
```

### search_listings — no matches

```text
$ python -c "from tools import search_listings; print(search_listings('zzzznomatch', max_price=5))"
[]
```

### search_listings — size filtering

```text
$ python -c "from tools import search_listings; print([(item['title'], item['size'], item['price']) for item in search_listings('graphic tee', size='M', max_price=30)])"
[('Y2K Baby Tee — Butterfly Print', 'S/M', 18.0), ('Mesh Long-Sleeve Top — Black', 'S/M', 15.0)]
```

The mesh top also matches because its description contains the search keywords. This search ranks keyword overlap; it does not determine whether the listing itself is a tee.

### suggest_outfit — initial development result

```text
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
None
```

This earlier run returned None. The later run below returned outfit suggestions; this log alone does not establish the cause of the earlier result.

### suggest_outfit — example wardrobe

```text
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Here are two outfit suggestions featuring your Vintage Levi's 501 Jeans:

### Outfit 1: Casual Streetwear & Basics
* **Selected Item:** Vintage Levi's 501 Jeans — Medium Wash
* **Wardrobe Pieces Used:** 
  * **White ribbed tank top** (w_003)
  * **Chunky white sneakers** (w_007)
  * **Black crossbody bag** (w_010)
* **Optional (Not part of supplied wardrobe):** A simple silver chain necklace.

**Why they work together:** 
This is a classic, effortless combination. The fitted white ribbed tank top contrasts nicely with the straight-leg fit of the vintage Levi's, creating a balanced silhouette. The chunky white sneakers tie in with the white top for a cohesive look, while the black crossbody bag adds a practical, minimal touch that fits the streetwear vibe of the jeans.

---

### Outfit 2: Cozy & Edgy Layering
* **Selected Item:** Vintage Levi's 501 Jeans — Medium Wash
* **Wardrobe Pieces Used:** 
  * **Oversized grey crewneck sweatshirt** (w_004)
  * **Black combat boots** (w_008)
  * **Brown leather belt** (w_009)
* **Optional (Not part of supplied wardrobe):** A plain white t-shirt to layer underneath the crewneck for a peek-of-white detail.

**Why they work together:**
This outfit plays with proportions by pairing the structured, straight-leg denim with an oversized grey crewneck sweatshirt. Adding the brown leather belt helps define the waist and breaks up the tones of the grey top and blue jeans. Finally, the black combat boots ground the outfit with a touch of grunge, complementing the vintage, broken-in aesthetic of the 501s.
```

### suggest_outfit — empty wardrobe

```text
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_empty_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_empty_wardrobe()))"
Here are two ways to style the **Vintage Levi's 501 Jeans (Medium Wash)**:

### Look 1: Casual & Classic Streetwear
Lean into the vintage roots of the jeans with a relaxed, effortless everyday outfit. 
* **Top:** A crisp white crewneck t-shirt or a vintage band tee.
* **Outerwear:** An oversized black or dark brown leather biker jacket.
* **Footwear:** Classic canvas sneakers (like white Converse or black-and-white Vans).
* **Accessories:** A simple black leather belt and a canvas tote bag.
* **Color Palette:** White, black, and medium blue indigo.

### Look 2: Smart-Casual Prep
Dress up the medium-wash denim by pairing it with tailored, structured pieces.
* **Top:** A light blue or white button-down oxford shirt, tucked in loosely.
* **Layer:** A neutral-toned knit sweater (like oatmeal, camel, or grey) draped over the shoulders.
* **Footwear:** Leather loafers or suede Chelsea boots.
* **Accessories:** A minimalist silver watch and a structured leather belt matching the shoes.
* **Color Palette:** Oatmeal, camel, white, and shades of blue.
```

### create_fit_card — initial caption

```text
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('Pair with a white ribbed tank top and chunky white sneakers.', load_listings()[0]))"
Nothing beats the timeless look of a great pair of worn-in denim, and these Vintage Levi's 501 Jeans — Medium Wash have that ideal laid-back vibe. I love styling them with a simple white ribbed tank top and chunky white sneakers for an effortless weekend outfit. Grab these today on depop for just $38.00 before they're gone!
```

### create_fit_card — whitespace-only outfit

```text
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('   ', load_listings()[0]))"
Cannot create a fit card because no outfit suggestion was provided.
```

### Caption variation — three fresh calls

Caching was disabled for this command.

```text
$ AI201_CACHE=0 python - <<'PY'
from tools import create_fit_card
from utils.data_loader import load_listings

item = load_listings()[0]
outfit = "Pair with a white ribbed tank top and chunky white sneakers."

for trial in range(1, 4):
    print(f"\n--- Caption {trial} ---")
    print(create_fit_card(outfit, item))
PY

--- Caption 1 ---
Nothing beats the effortless look of classic denim for everyday wear. Style these Vintage Levi's 501 Jeans — Medium Wash with a crisp white ribbed tank top and chunky white sneakers for an easy, streetwear-inspired fit. Grab them now for just $38.00 before they drop on depop!

--- Caption 2 ---
I am obsessed with the effortless cool of these Vintage Levi's 501 Jeans — Medium Wash, which are listed on depop for just $38.00. I love styling them with a classic white ribbed tank top and chunky white sneakers for the ultimate off-duty look. Grab this timeless denim staple before it's gone!

--- Caption 3 ---
Nothing beats a timeless pair of denim for effortless everyday styling. Grab these Vintage Levi's 501 Jeans — Medium Wash for $38.00 on depop to complete your look. Pair them with a simple white ribbed tank top and chunky white sneakers for a fresh, casual vibe.
```

### Prompt revision and fresh check

The first caption above invented a release claim: "before they drop on depop." The second used unsupported urgency: "before it's gone." I added this instruction to the caption prompt: "Do not invent release dates, availability, scarcity, discounts, or urgency to buy."

```text
$ AI201_CACHE=0 python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('Pair with a white ribbed tank top and chunky white sneakers.', load_listings()[0]))"
Elevate your everyday rotation with the Vintage Levi's 501 Jeans — Medium Wash, available now on depop for $38.00. For an effortless weekend look, pair them with a simple white ribbed tank top and chunky white sneakers.
```

The fresh result removed the future-release claim but still said "available now." This one run does not prove that unsupported availability claims have been eliminated.

---

## How I Used AI

### Moment 1 — Implementing and checking search

- **What I asked for:** I shared the starter files with ChatGPT and asked where to put the search implementation.
- **What came back:** ChatGPT give keyword scoring, size matching, and price filtering code, then helped identify indentation errors from my screenshots.
- **What I changed:** I inserted the implementation in tools.py, corrected its indentation, and ran the syntax and search checks. The actual outputs are recorded above.

### Moment 2 — Reviewing generated captions

- **What I asked for:** I shared three generated captions with ChatGPT and asked for the next step.
- **What came back:** ChatGPT identified an unsupported release claim and suggested a prompt instruction against invented release dates, availability, scarcity, discounts, and urgency.
- **What I changed:** I added the instruction and generated a fresh caption with caching disabled. I preserved the original results and the new result, including its remaining "available now" claim.

### Other AI assistance

ChatGPT also helped draft the tool specifications, acceptance criteria 3–5 and the reasons under the criteria, and the outfit and caption implementations. It helped organize the terminal output into this README. The recorded outputs came from my terminal runs.

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