
from context import build_deal_context
from gemini_advisor import analyze_deal


def build_context(title, proposed_price):
    context = build_deal_context(title, proposed_price)
    return context

# Funcoes de leitura/validacao sempre devem ou retornar um erro claro, ou o valor validado.
def read_proposed_price():
    raw_price = input("Enter a proposed price: ").strip().replace(",", ".")
    try:
        proposed_price = float(raw_price)
    except ValueError:
        raise ValueError("Invalid price. Please enter a valid number.")

    if proposed_price < 0:
        raise ValueError("Price cannot be negative.")
        
    return proposed_price

def read_title():
    title = input("Enter the game title: ").strip()

    if not title:
        raise ValueError("Title cannot be empty.")
    
    return title

def main():
    while True:
        print("""
            1 - Type a game title and proposed price to analyze a deal
            2 - Exit""")
        choice = input("Enter your choice: ").strip()
        
        if choice == "2":
            break
    
        elif choice == "1":
            try:
                title = read_title()
                proposed_price = read_proposed_price()
                ctx = build_context(title, proposed_price)
                advice = analyze_deal(ctx)

                for key, value in advice.items():
                    if key == "key_insights":
                        print("KEY INSIGHTS:")
                        for insight in value:
                            print(f"  - {insight}")
                    else:
                        print(f"{key}: {value}")
                    
            except ValueError as error: 
                print(f"{error}")
                continue
            except Exception as error:
                print(f"An unexpected error occurred: {error}")
                continue
    
        else:
            print("Invalid choice. Please enter 1 or 2.")
            continue

if __name__ == "__main__":
    main()