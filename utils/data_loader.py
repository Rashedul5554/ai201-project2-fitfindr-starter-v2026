"""
Utility functions for loading the mock listings dataset and wardrobe schema.
Use these in your tool implementations to access the data without re-reading
the files each time.
"""

import json
import os
from typing import Optional

# Resolve the path to the data directory relative to this file
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_listings() -> list[dict]:
    """
    Load all mock listings from the dataset.

    Returns:
        A list of listing dictionaries. Each listing has the following fields:
        - id (str)
        - title (str)
        - description (str)
        - category (str): one of tops, bottoms, outerwear, shoes, accessories
        - style_tags (list[str])
        - size (str)
        - condition (str): excellent, good, or fair
        - price (float)
        - colors (list[str])
        - brand (str or None)
        - platform (str): depop, thredUp, or poshmark
    """
    path = os.path.join(_DATA_DIR, "listings.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_wardrobe_schema() -> dict:
    """
    Load the wardrobe schema, including the example wardrobe and empty template.

    Returns:
        A dictionary containing:
        - schema: the field definitions for a wardrobe item
        - example_wardrobe: a sample wardrobe with 10 items
        - empty_wardrobe: a starting template for a new user
    """
    path = os.path.join(_DATA_DIR, "wardrobe_schema.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _wardrobe(name: str) -> dict:
    """
    Pull one wardrobe out of the schema file, without the documentation keys.

    The JSON uses underscore-prefixed keys (_description, _note) to explain
    itself to a human reader. Those are notes about the file, not part of a
    wardrobe, and stripping them here means both wardrobes below come back
    the same shape. Otherwise the empty one carries an extra _note key, and a
    tool that formats the whole dict into a prompt would send the model a
    sentence about templates.
    """
    wardrobe = load_wardrobe_schema()[name]
    return {k: v for k, v in wardrobe.items() if not k.startswith("_")}


def get_example_wardrobe() -> dict:
    """
    Convenience function — returns just the example wardrobe items list.

    Returns:
        A wardrobe dict with an 'items' key containing a list of wardrobe items.
    """
    return _wardrobe("example_wardrobe")


def get_empty_wardrobe() -> dict:
    """
    Convenience function — returns an empty wardrobe template.

    Returns:
        A wardrobe dict with an empty 'items' list. Same shape as the example
        wardrobe — the only difference is that 'items' is empty.
    """
    return _wardrobe("empty_wardrobe")

def save_wardrobe(wardrobe: dict) -> None:
    """Save a wardrobe so it can be used in another program run."""
    if not isinstance(wardrobe, dict):
        raise ValueError("The wardrobe must be a dictionary.")

    items = wardrobe.get("items")
    if not isinstance(items, list):
        raise ValueError("The wardrobe must contain an items list.")

    seen_ids = set()
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("Each wardrobe item must be a dictionary.")

        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id.strip():
            raise ValueError("Each wardrobe item needs a non-empty string ID.")

        if item_id in seen_ids:
            raise ValueError(f"Duplicate wardrobe item ID: {item_id}")
        seen_ids.add(item_id)

    # Convert before opening the file so invalid data cannot erase a save.
    contents = json.dumps(wardrobe, indent=2, ensure_ascii=False)
    path = os.path.join(_DATA_DIR, "my_wardrobe.json")
    temporary_path = path + ".tmp"

    with open(temporary_path, "w", encoding="utf-8") as f:
        f.write(contents)
        f.write("\n")

    os.replace(temporary_path, path)


def load_saved_wardrobe() -> dict:
    """Load the saved wardrobe, or the example if no save exists."""
    path = os.path.join(_DATA_DIR, "my_wardrobe.json")

    try:
        with open(path, "r", encoding="utf-8") as f:
            wardrobe = json.load(f)
    except FileNotFoundError:
        return get_example_wardrobe()

    if not isinstance(wardrobe, dict):
        raise ValueError("The saved wardrobe must be a dictionary.")

    if not isinstance(wardrobe.get("items"), list):
        raise ValueError("The saved wardrobe must contain an items list.")

    if not all(isinstance(item, dict) for item in wardrobe["items"]):
        raise ValueError("Each saved wardrobe item must be a dictionary.")

    return wardrobe


# --- Quick sanity check ---
if __name__ == "__main__":
    listings = load_listings()
    print(f"Loaded {len(listings)} listings.")
    print(f"First listing: {listings[0]['title']} — ${listings[0]['price']}")

    wardrobe = get_example_wardrobe()
    print(f"\nExample wardrobe has {len(wardrobe['items'])} items.")
    print(f"First item: {wardrobe['items'][0]['name']}")
