# qmu_dimensional_analysis.py

from qmu_units import all_units, QMUQuantity, QMUUnit, simplify_and_match_unit
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

        print(f"Debug: Result before simplification: {result}")  

        if isinstance(result, QMUQuantity):
            simplified_unit = simplify_and_match_unit(result.unit)
            print(f"Debug: Simplified unit: {simplified_unit.symbol}")
            return QMUQuantity(result.value, simplified_unit)
        else:
            raise ValueError(f"Unexpected result type from operation: {type(result)}")
    except (TypeError, ValueError) as e:
        return str(e)

def main():
    print("QMU Dimensional Analysis System")
    print("===============================")
    
    while True:
        print("\n1. Perform dimensional analysis")
        print("2. Search for a unit")
        print("3. Display units by category")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            unit1 = input("Enter first unit symbol: ")
            value1 = float(input("Enter first value: "))
            unit2 = input("Enter second unit symbol: ")
            value2 = float(input("Enter second value: "))
            operation = input("Enter operation (+, -, *, /): ")
            
            if unit1 in all_units and unit2 in all_units:
                quantity1 = QMUQuantity(value1, all_units[unit1])
                quantity2 = QMUQuantity(value2, all_units[unit2])
                
                result = dimensional_analysis(quantity1, quantity2, operation)
                if isinstance(result, str):  # Error message
                    print(f"Error: {result}")
                else:
                    print(f"Result: {result}")
            else:
                print("Invalid unit symbol(s). Please try again.")
        
        elif choice == '2':
            query = input("Enter unit name or symbol to search: ")
            results = search_unit(query)
            if results:
                print("\nSearch Results:")
                for unit in results:
                    print(f"{unit.symbol}: {unit.name}")
            else:
                print("No units found matching your search.")
        
        elif choice == '3':
            categorize_units()  # Ensure units are categorized
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
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
