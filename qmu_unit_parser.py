import os
import json
import re
import glob

def parse_qmu_units(file_paths):
    units = {}
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            content = file.read()

        current_unit = None
        current_section = None

        for line in content.split('\n'):
            if line.strip() == '':
                continue

            if line.startswith('# '):
                if current_unit:
                    units[current_unit['symbol']] = current_unit
                unit_name = line[2:].strip()
                symbol_match = re.search(r'\((\w+)\)', unit_name)
                if symbol_match:
                    symbol = symbol_match.group(1)
                    name = unit_name.split('(')[0].strip()
                else:
                    symbol = name = unit_name
                current_unit = {
                    'name': name,
                    'symbol': symbol,
                    'expression': '',
                    'si_equivalent': '',
                    'shorthand': '',
                    'description': '',
                    'relationships': '',
                    'applications': '',
                    'other_info': ''
                }
                current_section = None
            elif line.startswith('## '):
                current_section = line[3:].strip().lower()
            elif current_unit and current_section:
                if current_section == 'qmu expression':
                    current_unit['expression'] += line.strip() + ' '
                elif current_section == 'si equivalent':
                    current_unit['si_equivalent'] += line.strip() + ' '
                elif current_section == 'shorthand':
                    current_unit['shorthand'] += line.strip() + ' '
                elif current_section in current_unit:
                    current_unit[current_section] += line.strip() + '\n'

        if current_unit:
            units[current_unit['symbol']] = current_unit

    return units

def generate_json(units, output_file):
    json_data = {symbol: {k: v.strip() for k, v in unit.items() if k != 'symbol'} 
                 for symbol, unit in units.items()}
    
    with open(output_file, 'w') as file:
        json.dump(json_data, file, indent=2)

def generate_description_files(units, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    for symbol, unit in units.items():
        file_path = os.path.join(output_dir, f"{symbol}.txt")
        with open(file_path, 'w') as file:
            file.write(f"# {unit['name']} ({symbol})\n\n")
            file.write(f"QMU Expression: {unit['expression'].strip()}\n\n")
            file.write(f"SI Equivalent: {unit['si_equivalent'].strip()}\n\n")
            file.write(f"Shorthand: {unit['shorthand'].strip()}\n\n")
            file.write("## Description\n")
            file.write(unit['description'])
            file.write("\n\n## Relationships\n")
            file.write(unit['relationships'])
            file.write("\n\n## Applications\n")
            file.write(unit['applications'])
            file.write("\n\n## Other Information\n")
            file.write(unit['other_info'])

if __name__ == "__main__":
    input_files = glob.glob("input_data/qmu-units-part*.txt")
    json_output = "qmu_units.json"
    desc_output_dir = "unit_descriptions"

    units = parse_qmu_units(input_files)
    generate_json(units, json_output)
    generate_description_files(units, desc_output_dir)

    print(f"Processed {len(units)} units from {len(input_files)} input files.")
    print(f"JSON file created: {json_output}")
    print(f"Description files created in: {desc_output_dir}")
