"""Expose FitFindr search and price comparison through MCP over stdio."""
from mcp.server.fastmcp import FastMCP
from tools import search_listings as _search_listings_impl
from tools import compare_prices as _compare_prices_impl

mcp = FastMCP("fitfindr", log_level="WARNING")


@mcp.tool()
def search_listings(description: str, size: str | None = None,
                    max_price: float | None = None) -> list[dict]:
    """Search mock clothing listings using description keywords (string),
    optional size (string), and an inclusive max_price in US dollars (number).
    None skips the corresponding filter. Keywords match whole words in titles,
    descriptions and style tags, ignoring case; results rank by distinct keyword
    overlap, with original data order breaking ties. Size matches complete labels
    or slash-separated alternatives, ignoring case and parenthetical fit notes.
    Return up to the configured search limit of listing dictionaries containing
    id, title, description, category, style_tags, size, condition, price, colors,
    brand and platform; return an empty list when nothing matches.
    """
    return _search_listings_impl(description, size, max_price)


@mcp.tool()
def compare_prices(new_item: dict) -> dict:
    """Compare a selected listing with other mock listings in its category.
    new_item is an object with id (string), category (string), and price
    (number in US dollars). Exclude listings with the selected id.
    Return comparison_count (integer), median_price (US dollars), and
    price_difference (selected price minus median, in US dollars).
    Monetary results are rounded to two decimal places. With no comparisons,
    return comparison_count 0 and null for median_price and price_difference.
    This describes the local mock dataset, not live market prices.
    """
    return _compare_prices_impl(new_item)


if __name__ == "__main__":
    mcp.run(transport="stdio")
