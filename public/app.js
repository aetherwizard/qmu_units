document.addEventListener('DOMContentLoaded', () => {
    const unitList = document.getElementById('unit-list');
    const unitSearch = document.getElementById('unit-search');
    const unitName = document.getElementById('unit-name');
    const unitSymbol = document.getElementById('unit-symbol');
    const unitExpression = document.getElementById('unit-expression');
    const unitSIEquivalent = document.getElementById('unit-si-equivalent');
    const unitShorthand = document.getElementById('unit-shorthand');
    const description = document.getElementById('description');
    const saveBtn = document.getElementById('save-btn');

    let currentUnit = null;

    function loadUnits() {
        fetch('/api/units')
            .then(response => response.json())
            .then(units => {
                unitList.innerHTML = units.map(unit =>
                    `<option value="${unit.symbol}">${unit.name} (${unit.symbol})</option>`
                ).join('');
            });
    }

    function loadUnit(symbol) {
        fetch(`/api/unit/${symbol}`)
            .then(response => response.json())
            .then(unit => {
                currentUnit = unit;
                unitName.value = unit.name;
                unitSymbol.value = unit.symbol;
                unitExpression.value = unit.expression || '';
                unitSIEquivalent.value = unit.si_equivalent || '';
                unitShorthand.value = unit.shorthand || '';
                description.value = unit.description;
            });
    }

    unitSearch.addEventListener('change', (e) => {
        loadUnit(e.target.value);
    });

    saveBtn.addEventListener('click', () => {
        if (currentUnit) {
            const updatedUnit = {
                name: unitName.value,
                symbol: unitSymbol.value,
                expression: unitExpression.value,
                si_equivalent: unitSIEquivalent.value,
                shorthand: unitShorthand.value,
                description: description.value
            };

            fetch(`/api/unit/${currentUnit.symbol}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updatedUnit),
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        alert('Unit updated successfully!');
                        loadUnits(); // Reload the unit list to reflect any changes
                        loadUnit(updatedUnit.symbol); // Reload the current unit
                    } else {
                        alert('Failed to update unit: ' + result.message);
                    }
                });
        }
    });

    loadUnits();
});