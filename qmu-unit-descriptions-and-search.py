import os
import json
from qmu_units import all_units
from qmu_unit_categorization import categories, categorize_units

# Directory to store unit description files
UNIT_DESC_DIR = "unit_descriptions"

# Ensure the directory exists
os.makedirs(UNIT_DESC_DIR, exist_ok=True)

def create_unit_description_file(unit_code, unit):
    """Create an initial description file for a unit."""
    file_path = os.path.join(UNIT_DESC_DIR, f"{unit_code}.json")
    if not os.path.exists(file_path):
        initial_content = {
            "name": unit.name,
            "symbol": unit.symbol,
            "description": "Add a description of what this unit represents.",
            "usage": "Explain how this unit may be used.",
            "keywords": ["Add", "relevant", "keywords", "here"],
            "applications": ["List", "potential", "applications"],
            "related_units": ["List", "related", "units"]
        }
        with open(file_path, 'w') as f:
            json.dump(initial_content, f, indent=2)

def create_all_unit_description_files():
    """Create description files for all units."""
    for unit_code, unit in all_units.items():
        create_unit_description_file(unit_code, unit)

def read_unit_description(unit_code):
    """Read the description file for a unit."""
    file_path = os.path.join(UNIT_DESC_DIR, f"{unit_code}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return None

def update_unit_description(unit_code, new_content):
    """Update the description file for a unit."""
    file_path = os.path.join(UNIT_DESC_DIR, f"{unit_code}.json")
    with open(file_path, 'w') as f:
        json.dump(new_content, f, indent=2)

def search_units(query):
    """Search for units based on a query string."""
    results = []
    query = query.lower()
    for unit_code in all_units:
        description = read_unit_description(unit_code)
        if description:
            searchable_text = ' '.join(str(value) for value in description.values() if isinstance(value, (str, list)))
            if query in searchable_text.lower():
                results.append((unit_code, description))
    return results

def display_unit_info(unit_code):
    """Display detailed information about a unit."""
    description = read_unit_description(unit_code)
    if description:
        print(f"\nUnit: {description['name']} ({description['symbol']})")
        print(f"Description: {description['description']}")
        print(f"Usage: {description['usage']}")
        print(f"Keywords: {', '.join(description['keywords'])}")
        print(f"Applications: {', '.join(description['applications'])}")
        print(f"Related Units: {', '.join(description['related_units'])}")
    else:
        print(f"No description found for unit {unit_code}")

def main():
    create_all_unit_description_files()
    categorize_units()

    while True:
        print("\nQMU Unit Information System")
        print("1. Search for units")
        print("2. Display all units by category")
        print("3. Update unit description")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            query = input("Enter search query: ")
            results = search_units(query)
            if results:
                print("\nSearch Results:")
                for unit_code, description in results:
                    print(f"{unit_code}: {description['name']} ({description['symbol']})")
                unit_choice = input("Enter unit code for more info (or press Enter to skip): ")
                if unit_choice:
                    display_unit_info(unit_choice)
            else:
                print("No results found.")

        elif choice == '2':
            for category, units in categories.items():
                print(f"\n{category}:")
                for unit in units:
                    print(f"  {unit.symbol}: {unit.name}")

        elif choice == '3':
            unit_code = input("Enter unit code to update: ")
            if unit_code in all_units:
                description = read_unit_description(unit_code)
                if description:
                    print("Current description:")
                    display_unit_info(unit_code)
                    field = input("Enter field to update (description/usage/keywords/applications/related_units): ")
                    if field in description:
                        new_value = input(f"Enter new {field}: ")
                        if field in ['keywords', 'applications', 'related_units']:
                            new_value = [item.strip() for item in new_value.split(',')]
                        description[field] = new_value
                        update_unit_description(unit_code, description)
                        print("Description updated successfully.")
                    else:
                        print("Invalid field.")
                else:
                    print(f"No description found for unit {unit_code}")
            else:
                print("Invalid unit code.")

        elif choice == '4':
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
