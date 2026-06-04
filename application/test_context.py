from cmath import e
import json

from context import build_deal_context
from gemini_advisor import analyze_deal

def test_build_deal_context(title, proposed_price):
    context = build_deal_context(title, proposed_price)

    # SERIALIZES A NATIVE OBJECT (DICT, LISTS ETC) TO A FORMATTED JSON STRING
    return json.dumps(context, indent=4)

while True:
    print("""
        1 - Type a game title and proposed price to analyze a deal
        2 - Exit""")
    choice = input("Enter your choice: ")
    
    if choice == "2":
        break

    elif choice == "1":
        try:
            title = input("Enter a game title: ").strip()
            proposed_price = float(input("Enter a proposed price: "))
            ctx = test_build_deal_context(title, proposed_price)
            advice = analyze_deal(ctx)
            print(advice) # Melhorar isso
        except Exception as e: 
            print(f"An error occurred: {e}")
            continue

    else:
        print("Invalid choice. Please enter 1 or 2.")
        continue
