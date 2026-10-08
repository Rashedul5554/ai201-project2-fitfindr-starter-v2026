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
> The planning loop has been exercised with matching and empty-search queries.
> Price comparison is implemented and demonstrated below.
> The explicit wardrobe-content branch has been exercised with existing and empty wardrobes.
> Style memory saves wardrobe items between runs; a recorded check confirms the saved item reaches the outfit tool unchanged.
>
> **The rest of this file is your submission.** Fill it in as you go.

### Milestone 1 — Setup and data exploration

The environment check passed all 10 checks. I inspected six listings and the wardrobe fields. Listings include title, description, size, price, and style_tags. Prices are numbers, style_tags are lists, and sizes include formats such as S/M and XL (oversized).

I ran the query 'vintage graphic tee under $30'. The starter reported that the planning loop is not built yet, which is the expected starting behavior.

## Planned Unit 3 Stretch Features

The following declarations were recorded before implementation. They are retained here as the original plan.

**Current status:** Price comparison and the explicit wardrobe-content branch are implemented, with development runs recorded under Sample Run. Style memory is also implemented: separate commands saved and loaded the wardrobe, and a development check confirmed that the added scarf reached `suggest_outfit` unchanged. The Unit 3 output below is one development check; the later Unit 4 corrected baseline passed all five persistence trials.

- **Fourth tool — compare_prices:** Takes the selected listing and compares its price with other listings in the same category. Returns a dictionary containing the number of comparison items, their median price, and the selected item's difference from that median. If no comparison items exist, returns a count of zero and None for the median and difference. The agent will call this tool after selecting an item. Comparisons describe this dataset, not market value.

- **Second planning-loop branch — empty wardrobe:** If the wardrobe has no items, the loop will request general styling advice. Otherwise, it will request combinations using the user's stored wardrobe. I will record runs showing both paths.

- **Style memory:** Save user-provided wardrobe items locally between runs. I will demonstrate one run that stores a wardrobe change and a separate run that loads and uses that change.

The implementation and development output are recorded below; these declarations are retained as historical plans.

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

FitFindr accepts clothing requests such as "a vintage graphic tee under $30, size M" and searches a local mock listings dataset. It selects a matching item, suggests outfits using the supplied wardrobe, and generates a short caption. If no listings match, it stops and suggests changing the description, size, or budget. It also compares the selected item with other same-category listings and displays their median price and the difference from the selected price. The planning loop chooses combinations from the supplied wardrobe when it contains items, or general styling advice when it is empty. Wardrobe changes can be saved locally and loaded by later queries.



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

### `compare_prices`

- **What it does:** Compares the selected item's price with other listings in the same category, excluding the selected listing.
- **Inputs:** new_item (dict containing id, category, and price).
- **Returns:** A dictionary with comparison_count (int), median_price (number), and price_difference (number: selected price minus median). A negative difference means the selected item is cheaper.
- **When it has nothing:** Returns comparison_count of 0 and None for median_price and price_difference.

This compares the local dataset, not market value. The agent calls it after selecting an item and saves the result in session["price_comparison"].


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

**Branch rule:** If search_listings returns an empty list, save a message in the session suggesting that the user change the description, size, or budget, then stop without calling suggest_outfit or create_fit_card. Otherwise, save the first matching listing in the session as selected_item, call compare_prices with that item and save the comparison, then pass the saved item to suggest_outfit, save the outfit suggestion, and use the saved suggestion and item to call create_fit_card. Save the resulting fit card in the session.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regular expressions extract a price ceiling after “under,” “below,” or “up to,” and a size after “size.” Leading request phrases and commas are removed from the remaining text to form the search description. This parser supports these documented formats rather than arbitrary natural-language requests.

**What moves through the session:** Parsed inputs are saved in `parsed`. Search results are saved in `search_results`, and the first result becomes `selected_item`. The price-comparison tool reads `selected_item` and saves its result in `price_comparison`. The wardrobe branch saves `styling_mode` as `wardrobe_combinations` or `general_advice`. The outfit tool reads `selected_item` and `wardrobe` from the session and saves its response in `outfit_suggestion`. The caption tool reads `outfit_suggestion` and `selected_item`, then saves its response in `fit_card`. An empty search sets `error` and stops the loop. Empty outfit or caption responses also set `error`.

**Loop control:** The loop advances through `parse`, `search`, `compare`, and `choose_styling`, then either `outfit` or `general_advice`, and finally `caption`. An empty search stops at the search stage. It calls `trace.check_iterations()` on each iteration to enforce the configured iteration limit.

**Wardrobe persistence:** `app.py::cmd_wardrobe_add` loads the current wardrobe, adds an item with a unique ID, and calls `utils/data_loader.py::save_wardrobe` to save it in `data/my_wardrobe.json`. Normal queries load that file through `load_saved_wardrobe` and pass the wardrobe to `run_agent`. If no saved file exists, the example wardrobe is used. `--empty-wardrobe` uses the empty template for that query without overwriting the saved file.

**Second branch — wardrobe contents:** In agent.py::run_agent, the choose_styling stage checks whether session["wardrobe"]["items"] contains any items. If it does, the loop sets styling_mode to wardrobe_combinations and moves to the outfit stage. Otherwise, it sets styling_mode to general_advice and moves to the general_advice stage. Both paths save the tool response in outfit_suggestion before continuing to the caption stage.

---

## Sample Run

These are actual development runs and clearly labeled excerpts from my terminal. They are not the Unit 4 acceptance evaluation.

### Style memory — saved wardrobe used in a later run

I saved a blue cotton scarf in one process, then loaded the wardrobe and ran a query in separate processes. The first save kept the ten example items and added the scarf.

```text
python app.py wardrobe-add --id my_scarf_001 --name "Blue cotton scarf" --category accessories --colors blue
Saved Blue cotton scarf (my_scarf_001) to data/my_wardrobe.json.
Wardrobe now contains 11 items.
```

`python app.py wardrobe` printed all 11 items. This is the added item's exact excerpt from that output:

```json
    {
      "id": "my_scarf_001",
      "name": "Blue cotton scarf",
      "category": "accessories",
      "colors": [
        "blue"
      ],
      "style_tags": []
    }
```

The subsequent query produced this output:

```text
python app.py ask 'vintage graphic tee under $30, size M'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Price comparison (same-category dataset listings):
    Other listings: 14
    Median price: $21.50
    Selected price minus median: $-3.50

  Outfit:   Here are two outfit suggestions featuring the Y2K Baby Tee with the butterfly print, using pieces from your wardrobe:

### Outfit 1: Y2K Streetwear Contrast
* **Selected Item:** Y2K Baby Tee — Butterfly Print
* **Wardrobe Pieces:**
  * **Baggy straight-leg jeans, dark wash** (`w_001`)
  * **Vintage black denim jacket** (`w_006`)
  * **Chunky white sneakers** (`w_007`)
  * **Black crossbody bag** (`w_010`)
* **Why it works:** This look leans into classic early-2000s proportions by pairing the fitted, cropped silhouette of the baby tee with the relaxed, low-to-mid hip drape of the baggy dark wash jeans. Layering theslightly cropped black denim jacket on top adds texture and edge, while the chunky white sneakers and black crossbody bag tie the retro streetwear aesthetic together.

---

### Outfit 2: Casual Earth-Tone Mix
* **Selected Item:** Y2K Baby Tee — Butterfly Print
* **Wardrobe Pieces:**
  * **Wide-leg khaki trousers** (`w_002`)
  * **Brown leather belt** (`w_009`)
  * **Chunky white sneakers** (`w_007`)
* **Optional (Not part of supplied wardrobe):** *Retro pastel pink shoulder bag*
* **Why it works:** The pink and purple butterfly graphic on the baby tee pops nicely against the neutral khaki of the wide-leg trousers. The fitted crop of the tee balances the looser volume of the trousers, andadding the brown leather belt pulls the look together with a neat, intentional finish. Chunky white sneakers keep the outfit grounded and casual.

  Fit card: Channel early-2000s proportions by pairing the Y2K Baby Tee — Butterfly Print with baggy straight-leg dark wash jeans and a vintage black denim jacket for added edge. This fitted crop top is availablefor $18.00 on depop. Finish the retro streetwear look with chunky white sneakers and a black crossbody bag.

2 model calls this session, 1476 prompt + 447 output tokens
```

I also observed the wardrobe passed to `suggest_outfit`, using a temporary wrapper that copied the input and then called the original function. The check compared the saved scarf against the item received by the tool:

```python
from copy import deepcopy
from unittest.mock import patch
import agent
from utils.data_loader import load_saved_wardrobe

wardrobe = load_saved_wardrobe()
saved_item = next(
    item for item in wardrobe["items"]
    if item["id"] == "my_scarf_001"
)
received = []
original = agent.suggest_outfit

def capture(new_item, wardrobe):
    received.append(deepcopy(wardrobe))
    return original(new_item, wardrobe)

with patch.object(agent, "suggest_outfit", side_effect=capture):
    session = agent.run_agent(
        "vintage graphic tee under $30, size M", wardrobe
    )

assert received, "The outfit tool was not called."
tool_item = next(
    item for item in received[0]["items"]
    if item["id"] == "my_scarf_001"
)
assert tool_item == saved_item, "The saved item's fields changed."
print("PASS: The saved scarf reached suggest_outfit unchanged.")
print("Saved item:", saved_item)
print("Tool received:", tool_item)
print("Agent error:", session["error"])
```

```text
PASS: The saved scarf reached suggest_outfit unchanged.
Saved item: {'id': 'my_scarf_001', 'name': 'Blue cotton scarf', 'category': 'accessories', 'colors': ['blue'], 'style_tags': []}
Tool received: {'id': 'my_scarf_001', 'name': 'Blue cotton scarf', 'category': 'accessories', 'colors': ['blue'], 'style_tags': []}
Agent error: None
```

The saved item reached the outfit tool unchanged. The model did not select the scarf in the recorded outfit, so this evidence establishes persistence and delivery to the tool, not that the scarf changed the recommendation. This is one development check; the later five-trial acceptance result is recorded under Run Log — Before. The generated text above is preserved as received, including spacing errors and its availability wording.

### Second-branch bonus — existing and empty wardrobes

I ran the same query with the example wardrobe and an empty wardrobe. Both returned an outfit and a fit card with `Error: None`, and the recorded styling modes differed as intended. These are development checks, not five-trial acceptance results. This command did not disable caching or print cache statistics.

```python
from agent import run_agent
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

for label, wardrobe in [
    ("Existing wardrobe", get_example_wardrobe()),
    ("Empty wardrobe", get_empty_wardrobe()),
]:
    session = run_agent("vintage graphic tee under $30, size M", wardrobe)
    print(f"\n=== {label} ===")
    print("Styling mode:", session["styling_mode"])
    print("Error:", session["error"])
    print("Outfit:", session["outfit_suggestion"])
    print("Fit card:", session["fit_card"])
```

The following are exact excerpts from the terminal output. The longer outfit descriptions are omitted from these excerpts.

```text
=== Existing wardrobe ===
Styling mode: wardrobe_combinations
Error: None
Outfit: Here are two outfit suggestions featuring your Y2K Butterfly Print Baby Tee, styled using pieces from your wardrobe.
```

```text
Fit card: Channeling early 2000s proportions is so easy with this Y2K Baby Tee — Butterfly Print, listed on depop for $18.00. I love styling it with baggy straight-leg dark wash jeans and chunky white sneakers for a classic streetwear vibe. It's a fun and effortless look for everyday wear!
```

```text
=== Empty wardrobe ===
Styling mode: general_advice
Error: None
Outfit: Here is some styling advice for the **Y2K Baby Tee with Butterfly Print**, along with a couple of outfit ideas built around its fitted, cropped silhouette and nostalgic color palette of white, pink, and purple.
```

```text
Fit card: Channel early 2000s nostalgia by pairing the Y2K Baby Tee — Butterfly Print with a high-waisted pleated tennis skirt in white or pastel pink for a sweet and casual everyday look. This fitted crop top isavailable on depop for $18.00. Add platform slides and butterfly hair clips to fully tie the retro theme together.
```

The existing-wardrobe output named supplied pieces and their IDs; the empty-wardrobe output gave general suggestions. The empty-wardrobe response also described the tee as cotton, which the listing description does not establish. Its caption contains the original spacing error “isavailable” and implies availability that the mock dataset cannot verify. I have preserved these results rather than correcting the generated text. These runs demonstrate the two paths, not that every generated claim is accurate or that wardrobe persistence works.

### Fourth-tool bonus — agent price comparison

```text
python -m py_compile app.py
python app.py ask 'vintage graphic tee under $30, size M'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Price comparison (same-category dataset listings):
    Other listings: 14
    Median price: $21.50
    Selected price minus median: $-3.50

  Outfit:   Here are two outfit suggestions featuring your Y2K Butterfly Print Baby Tee, styled using pieces from your wardrobe.

### Outfit 1: Classic Y2K Streetwear
* **Selected Item:** Y2K Baby Tee — Butterfly Print
* **Wardrobe Piece:** Baggy straight-leg jeans, dark wash (`w_001`)
* **Wardrobe Piece:** Chunky white sneakers (`w_007`)
* **Wardrobe Piece:** Black crossbody bag (`w_010`)
* **Optional (not part of wardrobe):** Silver chain necklace

**Why they work together:**
This look plays into classic early 2000s proportions. The fitted, cropped nature of the baby tee balances out the voluminous, high-waisted fit of the baggy dark wash jeans. The chunky white sneakers tie into the white base of the tee, while the black crossbody bag and optional silver accessories complete that effortless Y2K street style vibe.

---

### Outfit 2: Edgy Contrast
* **Selected Item:** Y2K Baby Tee — Butterfly Print
* **Wardrobe Piece:** Vintage black denim jacket (`w_006`)
* **Wardrobe Piece:** Wide-leg khaki trousers (`w_002`)
* **Wardrobe Piece:** Black combat boots (`w_008`)
* **Optional (not part of wardrobe):** Wire-rimmed sunglasses

**Why they work together:**
While the baby tee leans cute and graphic, pairing it with the vintage black denim jacket and black combat boots adds a touch of grunge and edge. The wide-leg khaki trousers bring in neutral earth tones that anchor the pink, purple, and white colors of the butterfly graphic, creating a fun mix of soft and tough aesthetics.

  Fit card: Channeling early 2000s proportions is so easy with this Y2K Baby Tee — Butterfly Print, listed on depop for $18.00. I love styling it with baggy straight-leg dark wash jeans and chunky white sneakers for a classic streetwear vibe. It's a fun and effortless look for everyday wear!

0 model calls this session, 2 served from cache
```

The selected tee costs $18.00, which is $3.50 below the $21.50 median of 14 other same-category listings. This adds dataset price context to the agent output; it does not estimate market value.


These are actual development runs copied from my terminal, including a full agent query and individual tool checks. They are not the Unit 4 acceptance evaluation. The two earlier full agent queries shown in the price-comparison and pre-comparison sections reused two cached model responses; the price comparison is calculated locally.

### Earlier full agent query — before price comparison

```text
python app.py ask 'vintage graphic tee under $30, size M'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here are two outfit suggestions featuring your Y2K Butterfly Print Baby Tee, styled using pieces from your wardrobe.

### Outfit 1: Classic Y2K Streetwear
* **Selected Item:** Y2K Baby Tee — Butterfly Print
* **Wardrobe Piece:** Baggy straight-leg jeans, dark wash (`w_001`)
* **Wardrobe Piece:** Chunky white sneakers (`w_007`)
* **Wardrobe Piece:** Black crossbody bag (`w_010`)
* **Optional (not part of wardrobe):** Silver chain necklace

**Why they work together:**
This look plays into classic early 2000s proportions. The fitted, cropped nature of the baby tee balances out the voluminous, high-waisted fit of the baggy dark wash jeans. The chunky white sneakers tie into the white base of the tee, while the black crossbody bag and optional silver accessories complete that effortless Y2K street style vibe.

---

### Outfit 2: Edgy Contrast
* **Selected Item:** Y2K Baby Tee — Butterfly Print
* **Wardrobe Piece:** Vintage black denim jacket (`w_006`)
* **Wardrobe Piece:** Wide-leg khaki trousers (`w_002`)
* **Wardrobe Piece:** Black combat boots (`w_008`)
* **Optional (not part of wardrobe):** Wire-rimmed sunglasses

**Why they work together:**
While the baby tee leans cute and graphic, pairing it with the vintage black denim jacket and black combat boots adds a touch of grunge and edge. The wide-leg khaki trousers bring in neutral earth tones that anchor the pink, purple, and white colors of the butterfly graphic, creating a fun mix of soft and tough aesthetics.

  Fit card: Channeling early 2000s proportions is so easy with this Y2K Baby Tee — Butterfly Print, listed on depop for $18.00. I love styling it with baggy straight-leg dark wash jeans and chunky white sneakers for a classic streetwear vibe. It's a fun and effortless look for everyday wear!

0 model calls this session, 2 served from cache
```


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

I used ChatGPT for implementation help, debugging, test design, and documentation. The examples below describe the assistance and how I checked it. Recorded outputs came from my terminal runs.

### Moment 1 — Implementing and checking search

- **What I asked for:** Help placing the search implementation in the starter code.
- **What came back:** Keyword scoring, size matching, and price filtering code, plus help identifying indentation errors from screenshots.
- **What I changed and checked:** I inserted the implementation in `tools.py`, corrected its indentation, and ran the syntax and search checks recorded above.

### Moment 2 — Reviewing generated captions

- **What I asked for:** A review of three generated captions and advice on the next step.
- **What came back:** Identification of an unsupported release claim and a proposed prompt instruction against invented availability, release dates, scarcity, discounts, and urgency.
- **What I changed and checked:** I added the instruction and generated a fresh caption with caching disabled. I preserved both the original results and the new result, including its remaining “available now” claim.

### Other assistance and verification

AI assistance also covered the tool specifications, stretch-feature plans, acceptance criteria 3–5 and criterion rationales, tool and planning-loop implementations, command-line changes, wardrobe persistence, and the saved-item check. For Unit 4, it covered MCP registration and integration, tracing, model-error handling, the evaluation runner, the fixed caption-detail test, evidence review, and README organization.

I installed the changes and ran the checks documented here. The initial AI-provided persistence test omitted required dataset fixtures from its temporary directory. I preserved that failed evaluation, applied the correction, and reran all 25 trials. The error and correction are explained below. The proposed availability-prompt revision has not yet been verified with after-run evidence.

---

## Run Log — Before

The corrected baseline was recorded on October 7, 2026, with `python run_eval.py --label before_corrected`. Caching was disabled. Each original criterion was tested five times; the original targets in `criteria.md` are unchanged. PASS/FAIL decisions below were assigned by reviewing the saved evidence, not by the runner.

[Full corrected report](results/eval_20261007_191301_464195_before_corrected/report.md). The same directory contains one JSON evidence file per trial.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected item is preserved | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Accurate short fit card | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Wardrobe persists across processes | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

### Correction to the evaluation setup

The [original baseline](results/eval_20261007_185722_059121_before/report.md) is retained. Its five persistence trials stopped before `suggest_outfit` because `run_eval.py::worker` redirected the shared data directory to a temporary folder that did not contain `listings.json`. Search through MCP succeeded, but the local `tools.py::compare_prices` called `load_listings` against that temporary folder and raised `FileNotFoundError`.

These were invalid persistence trials caused by the evaluation setup; they do not establish a failure in wardrobe persistence. Commit `0afb690` copied the listings and wardrobe-schema fixtures into the isolated directory before starting the workers. I then reran all 25 trials into a new folder. The original evidence was not overwritten. This correction is not the measured agent improvement required later in Unit 4.

### Evidence excerpts from the corrected baseline

These are excerpts from the saved JSON records, not additional terminal runs. The full records linked below retain the complete inputs, outputs, and traces.

**Criterion 1, try 1 — Matching query completes.** Source: `agent.py::run_agent`, including `tools.py::create_fit_card`. [Full trial](results/eval_20261007_191301_464195_before_corrected/criterion_1_try_1.json).

```json
{
  "calls": [
    "search_listings (MCP)",
    "suggest_outfit",
    "create_fit_card"
  ],
  "fit_card": "Channel total early 2000s energy by styling the Y2K Baby Tee — Butterfly Print with dark wash baggy straight-leg jeans and chunky white sneakers for a cool streetwear contrast. This cute graphic top is available on depop for $18.00.",
  "error": null
}
```

**Criterion 2, try 1 — Impossible query stops.** Source: `agent.py::run_agent` empty-search branch. [Full trial](results/eval_20261007_191301_464195_before_corrected/criterion_2_try_1.json).

```json
{
  "calls": [
    "search_listings (MCP)"
  ],
  "search_return": [],
  "error": "No matching listings were found. Try different description keywords, another size, or a higher budget.",
  "fit_card": null
}
```

**Criterion 3, try 1 — Selected item is preserved.** Source: `agent.py::run_agent`, observed by `run_eval.py::agent_trial`. [Full trial](results/eval_20261007_191301_464195_before_corrected/criterion_3_try_1.json).

```json
{
  "search_return[0]": {
    "id": "lst_002",
    "title": "Y2K Baby Tee — Butterfly Print",
    "description": "Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.",
    "category": "tops",
    "style_tags": [
      "y2k",
      "vintage",
      "graphic tee",
      "cottagecore"
    ],
    "size": "S/M",
    "condition": "excellent",
    "price": 18.0,
    "colors": [
      "white",
      "pink",
      "purple"
    ],
    "brand": null,
    "platform": "depop"
  },
  "session.selected_item": {
    "id": "lst_002",
    "title": "Y2K Baby Tee — Butterfly Print",
    "description": "Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.",
    "category": "tops",
    "style_tags": [
      "y2k",
      "vintage",
      "graphic tee",
      "cottagecore"
    ],
    "size": "S/M",
    "condition": "excellent",
    "price": 18.0,
    "colors": [
      "white",
      "pink",
      "purple"
    ],
    "brand": null,
    "platform": "depop"
  },
  "outfit_inputs[0].new_item": {
    "id": "lst_002",
    "title": "Y2K Baby Tee — Butterfly Print",
    "description": "Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.",
    "category": "tops",
    "style_tags": [
      "y2k",
      "vintage",
      "graphic tee",
      "cottagecore"
    ],
    "size": "S/M",
    "condition": "excellent",
    "price": 18.0,
    "colors": [
      "white",
      "pink",
      "purple"
    ],
    "brand": null,
    "platform": "depop"
  }
}
```

**Criterion 4, try 1 — Accurate short fit card.** Source: `tools.py::create_fit_card`, called by `run_eval.py::caption_trial`. [Full trial](results/eval_20261007_191301_464195_before_corrected/criterion_4_try_1.json).

```json
{
  "source": "tools.py::create_fit_card",
  "new_item": {
    "id": "lst_001",
    "title": "Vintage Levi's 501 Jeans — Medium Wash",
    "description": "Classic 501s in a perfect medium wash. Some light fading at the knees which adds to the vintage look. No rips or stains.",
    "category": "bottoms",
    "style_tags": [
      "vintage",
      "classic",
      "denim",
      "streetwear"
    ],
    "size": "W30 L30",
    "condition": "good",
    "price": 38.0,
    "colors": [
      "blue",
      "indigo"
    ],
    "brand": "Levi's",
    "platform": "depop"
  },
  "outfit": "Style this item with neutral colors and simple accessories.",
  "fit_card": "Elevate your everyday rotation with the Vintage Levi's 501 Jeans — Medium Wash, available now on depop for $38.00. Pair them with neutral colors and simple accessories for an effortlessly classic look. It is a versatile denim staple that brings authentic character to any wardrobe."
}
```

**Criterion 5, try 1 — Wardrobe persists across processes.** Source: `utils/data_loader.py::save_wardrobe` and `load_saved_wardrobe`, followed by `agent.py::run_agent`; captured by `run_eval.py`. [Full trial](results/eval_20261007_191301_464195_before_corrected/criterion_5_try_1.json).

```json
{
  "expected_added_item": {
    "id": "eval_added_1",
    "name": "Evaluation scarf 1",
    "category": "accessories",
    "colors": [
      "blue"
    ],
    "style_tags": [
      "casual"
    ]
  },
  "save_process": {
    "pid": 12237,
    "operation": "save_wardrobe"
  },
  "load_process_pid": 12238,
  "saved_item": {
    "id": "eval_added_1",
    "name": "Evaluation scarf 1",
    "category": "accessories",
    "colors": [
      "blue"
    ],
    "style_tags": [
      "casual"
    ]
  },
  "loaded_item": {
    "id": "eval_added_1",
    "name": "Evaluation scarf 1",
    "category": "accessories",
    "colors": [
      "blue"
    ],
    "style_tags": [
      "casual"
    ]
  },
  "item_received_by_suggest_outfit": {
    "id": "eval_added_1",
    "name": "Evaluation scarf 1",
    "category": "accessories",
    "colors": [
      "blue"
    ],
    "style_tags": [
      "casual"
    ]
  }
}
```

---

## Verdicts and Diagnoses

1. **Criterion 1 — MET (5/5), target 4/5.** Every trial recorded search through MCP, outfit generation, and caption generation, returned a non-empty fit card, and ended with no session error.
2. **Criterion 2 — MET (5/5), target 5/5.** Every search returned an empty list. No outfit or caption call followed. Each result named description keywords, size, or budget as something the user could change.
3. **Criterion 3 — MET (5/5), target 5/5.** Full dictionary comparisons showed that the first search result, `session["selected_item"]`, and the actual `new_item` received by `suggest_outfit` had identical field values in every trial.
4. **Criterion 4 — MET (5/5), target 4/5.** Trials used five different listings. Sentence counts were 3, 3, 3, 2, and 3, excluding decimal points in prices. Every caption contained the correct listing title, price, and platform once each.
5. **Criterion 5 — MET (5/5), target 5/5.** The five distinct added items (`eval_added_1` through `eval_added_5`) matched in every field across saved data, loaded data, and the wardrobe received by `suggest_outfit`. Save and load used separate processes in every trial. This establishes persistence and delivery, not that the model chose the added item for an outfit.

**No original criterion was missed in the corrected baseline.** This does not establish that every behavior is correct. Criterion 4's quality bar is too limited: captions can meet the sentence and listing-fact requirements while giving generic styling advice or implying live availability. For example, its first trial says “available now,” which the mock dataset cannot verify. The existing criterion does not prohibit that wording, so the original verdict remains MET.

**Additional caption-detail check — MET (5/5), target 4/5.** I subsequently tested five fixed listing/outfit pairs with specific companion pieces and caching disabled. Each caption retained a supplied piece's color and clothing type. The evidence is recorded under The Improvement below. This check supplements the original criteria; it does not change their targets or verdicts. Since it already passed, detail retention is not the failure selected for improvement.

---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

These are actual Milestone 2 development runs from `app.py`, with steps recorded by `agent.py::run_agent` using `trace.step`. Caching was disabled for all four runs. These are not the five-trial acceptance evaluation. Trace values are shortened by the supplied trace formatter.

**Happy path**

```text
AI201_CACHE=0 python app.py ask 'vintage graphic tee under $30, size M' --trace
[1] parse_query
      in:  vintage graphic tee under $30, size M
      out: {'description': 'vintage graphic tee', 'size': 'M', 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': 'M', 'max_price': 30.0}
      out: 8 items: Y2K Baby Tee — Butterfly Print, Mesh Long-Sleeve Top — Black, 90s Silk Slip Dress — Floral, Midi Length … +5 more
[3] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] compare_prices
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: {'comparison_count': 14, 'median_price': 21.5, 'price_difference': -3.5}
[5] choose_styling
      in:  wardrobe items: 11
      out: wardrobe_combinations
      →    Next stage: outfit
[6] suggest_outfit
      in:  item=lst_002; wardrobe IDs=['w_001', 'w_002', 'w_003', 'w_004', 'w_005', 'w_006', 'w_007', 'w_008', 'w_009', '…
      out: Here are two outfit suggestions featuring your Y2K Baby Tee with the butterfly print, using pieces from the su…
      →    Styling mode: wardrobe_combinations
[7] create_fit_card
      in:  item=lst_002; outfit=Here are two outfit suggestions featuring your Y2K Baby Tee with the butterfly print, usi…
      out: Channel your inner early 2000s style by styling this sweet Y2K Baby Tee — Butterfly Print with high-waisted, b…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Price comparison (same-category dataset listings):
    Other listings: 14
    Median price: $21.50
    Selected price minus median: $-3.50

  Outfit:   Here are two outfit suggestions featuring your Y2K Baby Tee with the butterfly print, using pieces from the supplied wardrobe:

### Outfit 1: Classic Y2K Streetwear
* **Selected Item:** Y2K Baby Tee — Butterfly Print
* **Wardrobe Pieces Used:**
  * **Baggy straight-leg jeans, dark wash** (w_001)
  * **Chunky white sneakers** (w_007)
  * **Black crossbody bag** (w_010)
  * **Vintage black denim jacket** (w_006) *(Optional layer for cooler weather)*

**Why they work together:**
This combination leans directly into the Y2K aesthetic of the baby tee. The fitted, cropped silhouette of the butterfly tee creates a great proportion-play contrast when paired with the high-waisted, baggy straight-leg jeans. The chunky white sneakers tie in with the white base of the tee, while the black crossbody bag and optional cropped denim jacket keep the look cohesive and effortless. 

***

### Outfit 2: Casual Earth-Tone Contrast
* **Selected Item:** Y2K Baby Tee — Butterfly Print
* **Wardrobe Pieces Used:**
  * **Wide-leg khaki trousers** (w_002)
  * **Chunky white sneakers** (w_007)
  * **Brown leather belt** (w_009)
* **Optional (not part of the supplied wardrobe):** A small retro shoulder bag or delicate silver chain necklace to complement the early 2000s vibe.

**Why they work together:**
Pairing the sweet, pink-and-purple butterfly graphic tee with wide-leg khaki trousers bridges the gap between retro Y2K style and relaxed, minimal earth tones. Tucking the baby tee in and adding the brown leather belt pulls the waistline together, while the chunky white sneakers keep the outfit grounded, casual, and easy to wear day-to-day.

  Fit card: Channel your inner early 2000s style by styling this sweet Y2K Baby Tee — Butterfly Print with high-waisted, baggy straight-leg jeans for a classic streetwear proportion play. It is listed on depopfor $18.00 and brings an effortless retro vibe to your everyday wardrobe.

2 model calls this session, 1519 prompt + 485 output tokens
```

**Empty search**

```text
AI201_CACHE=0 python app.py ask 'zzzznomatch under $5' --trace
[1] parse_query
      in:  zzzznomatch under $5
      out: {'description': 'zzzznomatch', 'size': None, 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'zzzznomatch', 'size': None, 'max_price': 5.0}
      out: [] (empty)
[3] empty_search
      →    No matching listings were found. Try different description keywords, another size, or a higher budget.

  No matching listings were found. Try different description keywords, another size, or a higher budget.

0 model calls this session
```

**Empty wardrobe**

```text
AI201_CACHE=0 python app.py ask 'vintage graphic tee under $30, size M' --empty-wardrobe --trace
(running with an empty wardrobe)
[1] parse_query
      in:  vintage graphic tee under $30, size M
      out: {'description': 'vintage graphic tee', 'size': 'M', 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': 'M', 'max_price': 30.0}
      out: 8 items: Y2K Baby Tee — Butterfly Print, Mesh Long-Sleeve Top — Black, 90s Silk Slip Dress — Floral, Midi Length … +5 more
[3] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] compare_prices
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: {'comparison_count': 14, 'median_price': 21.5, 'price_difference': -3.5}
[5] choose_styling
      in:  wardrobe items: 0
      out: general_advice
      →    Next stage: general_advice
[6] suggest_outfit
      in:  item=lst_002; wardrobe IDs=[]
      out: Here is some styling advice for the **Y2K Baby Tee with Butterfly Print**, along with a couple of outfit sugge…
      →    Styling mode: general_advice
[7] create_fit_card
      in:  item=lst_002; outfit=Here is some styling advice for the **Y2K Baby Tee with Butterfly Print**, along with a c…
      out: Channel your inner 2000s icon by styling the Y2K Baby Tee — Butterfly Print with a pastel pink pleated tennis …

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Price comparison (same-category dataset listings):
    Other listings: 14
    Median price: $21.50
    Selected price minus median: $-3.50

  Outfit:   Here is some styling advice for the **Y2K Baby Tee with Butterfly Print**, along with a couple of outfit suggestions you can build to lean into its retro aesthetic!

### Styling Advice
* **Color Palette:** Since the tee features white, pink, and purple, you can easily pair it with matching pastel tones like lavender or baby pink, neutral bases like white or denim, or add contrast with dark charcoal grey and black for a classic Y2K edge.
* **Complementary Clothing Types:** 
  * *Bottoms:* Low-rise cargo pants, pleated mini skirts, wide-leg denim, or a slip skirt to play with proportions against the fitted, cropped silhouette.
  * *Footwear:* Chunky platform sneakers, strappy sandals, or retro platform mules.
  * *Accessories:* Small shoulder bags (baguette bags), beaded necklaces, or butterfly claw clips to complete the 2000s look.

---

### Outfit Suggestions

**Outfit 1: Casual Y2K Streetwear**
* **Top:** Y2K Baby Tee — Butterfly Print
* **Bottoms:** Relaxed, low-rise blue denim cargo pants
* **Footwear:** Chunky platform white sneakers
* **Accessories:** A small nylon shoulder bag and a metallic or beaded chain necklace

**Outfit 2: Sweet & Nostalgic**
* **Top:** Y2K Baby Tee — Butterfly Print
* **Bottoms:** A pastel pink or lavender pleated tennis skirt
* **Footwear:** Retro platform sandals or Mary Janes with white crew socks
* **Accessories:** Pastel butterfly hair clips and a simple pastel tote bag

  Fit card: Channel your inner 2000s icon by styling the Y2K Baby Tee — Butterfly Print with a pastel pink pleated tennis skirt and retro platform sandals for a sweet, nostalgic look. This cute cropped top is available right now on depop for $18.00. Grab it to add a playful touch of early-aughts charm to your everyday wardrobe!

2 model calls this session, 817 prompt + 416 output tokens
```

**Model unavailable**

```text
GEMINI_API_KEY=invalid-test-key AI201_CACHE=0 python app.py ask 'vintage graphic tee under $30, size M' --trace
[1] parse_query
      in:  vintage graphic tee under $30, size M
      out: {'description': 'vintage graphic tee', 'size': 'M', 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': 'M', 'max_price': 30.0}
      out: 8 items: Y2K Baby Tee — Butterfly Print, Mesh Long-Sleeve Top — Black, 90s Silk Slip Dress — Floral, Midi Length … +5 more
[3] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] compare_prices
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: {'comparison_count': 14, 'median_price': 21.5, 'price_difference': -3.5}
[5] choose_styling
      in:  wardrobe items: 11
      out: wardrobe_combinations
      →    Next stage: outfit
[6] suggest_outfit (failed)
      →    The model call for suggest_outfit failed. Check your internet connection and GEMINI_API_KEY in .env, run python test.py, then try again.

  The model call for suggest_outfit failed. Check your internet connection and GEMINI_API_KEY in .env, run python test.py, then try again.

1 model calls this session
```

**What these checks showed:** The normal run completed all four tools with two model calls. Empty search stopped before outfit generation with zero model calls. Empty wardrobe selected general advice and completed with two model calls. The invalid-key run stopped at `suggest_outfit` after one model call and gave recovery instructions without a traceback. The temporary environment variable affected only that command; the real `.env` key was not changed.

**Observation for later diagnosis:** The empty-wardrobe caption claimed the item was “available right now.” The mock listing does not establish live availability. I preserved that output; this observation is not a formal criterion verdict or a measured improvement.

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->

I registered search_listings in mcp_server.py and changed agent.py::run_agent to call it through mcp_client.call_tool. Its inputs are description (string), size (optional string), and max_price (optional number in US dollars).

I compared the MCP results with direct function results, including every returned field. Both checks passed:

    PASS: 'graphic tee' — 2 matching listings
    PASS: 'zzzznomatch' — 0 matching listings

The agent then completed the query 'vintage graphic tee under $30, size M', selecting the Y2K Baby Tee at $18.00 and returning an outfit and fit card. The outfit and caption reused two cached responses. These checks verified the MCP move; they were not acceptance-evaluation trials.


---

## The Improvement

**Status: baseline recorded; prompt change and after results pending.** Fixing the persistence-test fixtures repaired the evaluation setup and is not counted as the agent improvement.

### Caption-detail baseline

I ran `python check_caption_details.py --label before` with caching disabled. The five fixed listing/outfit pairs and unedited captions are saved in [the caption-detail report](results/caption_details_20261007_233127_495733_before/report.md). That directory also contains `evidence.json` and the tool implementation used in `tools_snapshot.py`. The baseline was committed as `869b9b3`.

Target: at least 4 of 5 captions recommend a supplied companion piece while retaining its color and clothing type. Equivalent wording is allowed; generic advice does not count.

1. **PASS:** “white ribbed tank top”
2. **PASS:** “wide-leg khaki trousers”
3. **PASS:** “black fitted turtleneck”
4. **PASS:** “charcoal joggers”
5. **PASS:** “cream cable-knit sweater”

**Verdict: MET (5/5).** The baseline already preserves concrete styling details, so I am not claiming a failure on this check.

### Availability wording check

After reviewing those outputs, I added a separate diagnostic target: **5 of 5 captions must avoid claiming current availability or inviting an immediate purchase, and must attribute price and platform to the supplied dataset.** This target was chosen after seeing the outputs and before the planned prompt revision. It does not replace an original acceptance criterion.

Applying this new rule retrospectively to the preserved baseline gives **MISSED (0/5)**:

1. **FAIL:** “available now on depop”
2. **FAIL:** “listed right now on depop”
3. **FAIL:** “Grab this versatile piece”
4. **FAIL:** “currently listed on poshmark”
5. **FAIL:** “available now on depop”

The captions also did not explicitly attribute the price and platform to the dataset. Their original detail-check verdicts remain PASS.

**Place and mechanism:** The issue occurs in the model output from `tools.py::create_fit_card`. The current prompt requests a natural social caption and prohibits invented availability, but does not explicitly identify the input as a mock dataset or require wording that attributes price and platform to it. The outputs show that the prohibition alone did not prevent live-marketplace language.

**Planned change:** Revise only the caption's system prompt to state that the data is a local mock dataset, require dataset attribution for price and platform, and explicitly prohibit availability claims and purchase invitations. Retain the exact-title, price, platform, sentence-count, and styling-detail requirements. This is a prompt-level attempt; its effectiveness still needs to be measured.

### Run Log — After

**Pending.** After changing the prompt, run:

```bash
python -m py_compile tools.py
python check_caption_details.py --label after
python run_eval.py --label after
```

Use the same five listing/outfit pairs and the same scoring rules. Compare availability wording and detail retention against the saved baseline, then score all five original criteria in the same table format as Run Log — Before. Record any regressions and preserve the generated outputs unchanged. No improvement is claimed until those results have been reviewed.

---

## What's Still Broken

- The original criteria all met their targets in this corrected baseline, but generated captions still imply live availability. Criterion 4, try 1 says “available now”; a local mock listing cannot establish that claim.
- The additional five-input caption-detail check passed, but those same outputs failed the newly defined availability-wording check. The prompt revision and after evaluation are still pending.
- Search uses keyword overlap and the query parser supports documented patterns. These 25 trials do not demonstrate handling of arbitrary phrasing, every size format, or every possible service failure.
- Passing the saved item into the outfit tool does not guarantee the model will include that item in its recommendation.

Unit 4 is still in progress: the improvement, after-run evidence, and final comparison remain to be completed before submission.

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