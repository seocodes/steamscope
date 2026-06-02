import json

from context import build_deal_context

def test_build_deal_context(title, proposed_price):
    context = build_deal_context(title, proposed_price)

    # SERIALIZES A NATIVE OBJECT (DICT, LISTS ETC) TO A FORMATTED JSON STRING
    return json.dumps(context, indent=4)

print(test_build_deal_context("No Man's Sky", 129.99))