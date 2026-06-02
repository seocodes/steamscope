import json

from context import build_deal_context
from gemini_advisor import analyze_deal

def test_build_deal_context(title, proposed_price):
    context = build_deal_context(title, proposed_price)

    # SERIALIZES A NATIVE OBJECT (DICT, LISTS ETC) TO A FORMATTED JSON STRING
    return json.dumps(context, indent=4)

ctx = test_build_deal_context("No Man's Sky", 59.99)
print(analyze_deal(ctx))

