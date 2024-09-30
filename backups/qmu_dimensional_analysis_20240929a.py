from qmu_units import all_units, QMUQuantity, QMUUnit, simplify_and_match_unit, get_unit_info
from qmu_categorization import categorize_units, get_units_by_category, search_unit, categories

def dimensional_analysis(quantity1, quantity2, operation):
    try:
        if operation == '+':
            result = quantity1 + quantity2
        elif operation == '-':
            result = quantity1 - quantity2
        elif operation == '*':
            result = quantity1 * quantity2
        elif operation == '/':
            result = quantity1 / quantity2
        else:
            raise ValueError("Unsupported operation")

        simplified_result = simplify_and_match_unit(result)
        return simplified_result
    except (TypeError, ValueError) as e:
        return str(e)

def search_and_display_unit_info(query):
    results = search_unit(query)
    if results:
        print(f"\nFound {len(results)} matching units:")
        for unit in results:
            print(f"\n{get_unit_info(unit.symbol)}")
    else:
        print(f"No units found matching '{query}'.")

def main():
    print("QMU Dimensional Analysis System")
    print("===============================")
    
    while True:
        print("\n1. Perform dimensional analysis")
        print("2. Search for a unit and display information")
        print("3. Display units by category")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            unit1 = input("Enter first unit symbol: ")
            if unit1 not in all_units:
                print(f"Error: '{unit1}' is not a valid unit symbol.")
                continue
            value1 = float(input("Enter first value: "))
            
            unit2 = input("Enter second unit symbol: ")
            if unit2 not in all_units:
                print(f"Error: '{unit2}' is not a valid unit symbol.")
                continue
            value2 = float(input("Enter second value: "))
            
            operation = input("Enter operation (+, -, *, /): ")
            
            quantity1 = QMUQuantity(value1, all_units[unit1])
            quantity2 = QMUQuantity(value2, all_units[unit2])
            
            result = dimensional_analysis(quantity1, quantity2, operation)
            if isinstance(result, str):
                print(f"Error: {result}")
            elif isinstance(result, QMUQuantity):
                print(f"Result: {result.value} {result.unit.symbol}")
            else:
                print(f"Unexpected result type: {type(result)}")
        
        elif choice == '2':
            query = input("Enter unit name or symbol to search: ")
            search_and_display_unit_info(query)
        
        elif choice == '3':
            categorize_units()
            category = input("Enter category name (or 'all' for all categories): ")
            if category.lower() == 'all':
                for cat in categories:
                    units = get_units_by_category(cat)
                    if units:
                        print(f"\n{categories[cat]}:")
                        for unit in units:
                            print(f"  {unit.symbol}: {unit.name}")
            elif category in categories:
                units = get_units_by_category(category)
                if units:
                    print(f"\n{categories[category]}:")
                    for unit in units:
                        print(f"  {unit.symbol}: {unit.name}")
                else:
                    print(f"No units found in category: {category}")
            else:
                print(f"Invalid category: {category}")
        
        elif choice == '4':
            break
        
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    main()
