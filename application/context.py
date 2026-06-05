try:
    from application.db import query_deals_by_title
except ModuleNotFoundError:
    from db import query_deals_by_title


def _ensure_float_price(value, field_name, title):
    try:
        return float(value)
    except (TypeError, ValueError): # Capturar somente o erro que esperamos
        raise ValueError(f"Invalid {field_name} for title '{title}': {value}")

def _average(values):
    return sum(values) / len(values)

def build_deal_context(title, proposed_price):
    if not title or not isinstance(title, str):
        raise ValueError("Title must be a non-empty string")

    proposed_price = _ensure_float_price(proposed_price, "proposed_price", title)
    deals = query_deals_by_title(title)

    if not deals:
        raise ValueError(f"No deals found for title '{title}'")
        
    dct_prices = [_ensure_float_price(deal.get("discounted_price"), "discounted_price", title) for deal in deals]
    discount_pcts = [_ensure_float_price(deal.get("discount_pct"), "discount_pct", title) for deal in deals]
    avg_dct_price = _average(dct_prices)
    avg_dct_pct = _average(discount_pcts)
    
    newest = deals[0]
    oldest = deals[-1]
    newest_scraped_at = newest.get("scraped_at")
    oldest_scraped_at = oldest.get("scraped_at")

    recent_snapshots = [
        {
            "scraped_at": deal.get("scraped_at"),
            "discounted_price": _ensure_float_price(deal.get("discounted_price"), "discounted_price", title),
            "discount_pct": _ensure_float_price(deal.get("discount_pct"), "discount_pct", title),
        } for deal in deals[:5]
    ]

    context = {
        "title": title,
        "proposed_discounted_price": round(proposed_price, 2),
        "history": {
            "scrape_count": len(deals),
            "date_range": {"first": oldest_scraped_at, "last": newest_scraped_at},
            "prices": {
                "min": round(min(dct_prices), 2),
                "max": round(max(dct_prices), 2),
                "avg": round(avg_dct_price, 2),
                "latest": round(_ensure_float_price(newest.get("discounted_price"), "discounted_price", title), 2),
            },
            "discount_pct": {
                "avg": round(avg_dct_pct, 2),
                "latest": round(_ensure_float_price(newest.get("discount_pct"), "discount_pct", title), 2),
            },
            "recent_snapshots": recent_snapshots,
        },
    }
    return context