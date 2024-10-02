const fs = require('fs');
const path = require('path');

class QMUUnit {
  constructor(name, symbol, expression = null, si_equivalent = null, shorthand = null) {
    this.name = name;
    this.symbol = symbol;
    this.expression = expression;
    this.si_equivalent = si_equivalent;
    this.shorthand = shorthand;
    this.description = this.loadDescription();
    this.base_units = this.parseExpression();
  }

  loadDescription() {
    const descriptionPath = path.join(__dirname, 'unit_descriptions', `${this.symbol}.txt`);
    if (fs.existsSync(descriptionPath)) {
      const content = fs.readFileSync(descriptionPath, 'utf8').trim();
      const startIndex = content.indexOf('## Description');
      const endIndex = content.indexOf('##', startIndex + 1);
      if (startIndex !== -1) {
        if (endIndex !== -1) {
          return content.slice(startIndex + 15, endIndex).trim();
        } else {
          return content.slice(startIndex + 15).trim();
        }
      }
    }
    return "No description available.";
  }

  parseExpression() {
    if (!this.expression) {
      return { [this.symbol]: 1 };
    }

    const base_units = {};
    const unit_pattern = /(me|λC|Fq|eemax)/g;
    const power_pattern = /\^(-?\d+)/;
    const parts = this.expression.split(/([*/])/);

    let current_op = '*';
    for (let part of parts) {
      if (part === '*' || part === '/') {
        current_op = part;
        continue;
      }

      part = part.replace(/[()]/g, '');
      const units = part.match(unit_pattern);

      if (units) {
        for (let unit of units) {
          const power_match = part.match(power_pattern);
          const power = power_match ? parseInt(power_match[1]) : 1;
          if (current_op === '*') {
            base_units[unit] = (base_units[unit] || 0) + power;
          } else {
            base_units[unit] = (base_units[unit] || 0) - power;
          }
        }
      }
    }

    return Object.fromEntries(Object.entries(base_units).filter(([_, value]) => value !== 0));
  }
}

class QMUQuantity {
  constructor(value, unit) {
    this.value = value;
    this.unit = unit;
  }

  toString() {
    return `${this.value} ${this.unit.symbol}`;
  }

  multiply(other) {
    if (other instanceof QMUQuantity) {
      const newValue = this.value * other.value;
      const newBaseUnits = {};
      for (const [unit, power] of Object.entries(this.unit.base_units)) {
        newBaseUnits[unit] = (newBaseUnits[unit] || 0) + power;
      }
      for (const [unit, power] of Object.entries(other.unit.base_units)) {
        newBaseUnits[unit] = (newBaseUnits[unit] || 0) + power;
      }
      const newExpression = Object.entries(newBaseUnits)
        .map(([unit, power]) => power === 1 ? unit : `${unit}^${power}`)
        .join('*');
      const newUnit = new QMUUnit("Custom Unit", newExpression, newExpression);
      return simplifyAndMatchUnit(new QMUQuantity(newValue, newUnit));
    } else if (typeof other === 'number') {
      return new QMUQuantity(this.value * other, this.unit);
    } else {
      throw new TypeError(`Multiplication not supported between QMUQuantity and ${typeof other}`);
    }
  }

  divide(other) {
    if (other instanceof QMUQuantity) {
      const newValue = this.value / other.value;
      const newBaseUnits = {};
      for (const [unit, power] of Object.entries(this.unit.base_units)) {
        newBaseUnits[unit] = (newBaseUnits[unit] || 0) + power;
      }
      for (const [unit, power] of Object.entries(other.unit.base_units)) {
        newBaseUnits[unit] = (newBaseUnits[unit] || 0) - power;
      }
      const newExpression = Object.entries(newBaseUnits)
        .map(([unit, power]) => power === 1 ? unit : `${unit}^${power}`)
        .join('*');
      const newUnit = new QMUUnit("Custom Unit", newExpression, newExpression);
      return simplifyAndMatchUnit(new QMUQuantity(newValue, newUnit));
    } else if (typeof other === 'number') {
      return new QMUQuantity(this.value / other, this.unit);
    } else {
      throw new TypeError(`Division not supported between QMUQuantity and ${typeof other}`);
    }
  }

  add(other) {
    if (!(other instanceof QMUQuantity)) {
      throw new TypeError(`Addition not supported between QMUQuantity and ${typeof other}`);
    }
    if (JSON.stringify(this.unit.base_units) !== JSON.stringify(other.unit.base_units)) {
      throw new Error(`Cannot add quantities with different units: ${this.unit.symbol} and ${other.unit.symbol}`);
    }
    return new QMUQuantity(this.value + other.value, this.unit);
  }

  subtract(other) {
    if (!(other instanceof QMUQuantity)) {
      throw new TypeError(`Subtraction not supported between QMUQuantity and ${typeof other}`);
    }
    if (JSON.stringify(this.unit.base_units) !== JSON.stringify(other.unit.base_units)) {
      throw new Error(`Cannot subtract quantities with different units: ${this.unit.symbol} and ${other.unit.symbol}`);
    }
    return new QMUQuantity(this.value - other.value, this.unit);
  }
}

class QMUDatabase {
  constructor() {
    this.units = {};
    this.loadUnits();
  }

  loadUnits() {
    const data = JSON.parse(fs.readFileSync(path.join(__dirname, 'qmu_units_data.json'), 'utf8'));

    // Load base units
    for (const [symbol, unit] of Object.entries(data.base_units)) {
      this.units[symbol] = new QMUUnit(unit.name, symbol, null, unit.si_equivalent);
    }

    // Load derived units
    for (const [symbol, unit] of Object.entries(data.derived_units)) {
      this.units[symbol] = new QMUUnit(unit.name, symbol, unit.expression, unit.si_equivalent);
    }

    // Load measurement units
    for (const [symbol, unit] of Object.entries(data.measurement_units)) {
      this.units[symbol] = new QMUUnit(unit.name, symbol, unit.expression);
    }
  }

  getUnit(symbol) {
    return this.units[symbol];
  }

  getAllUnits() {
    return this.units;
  }
}

function getUnitInfo(symbol) {
  const db = new QMUDatabase();
  const unit = db.getUnit(symbol);
  if (unit) {
    return `
Unit: ${unit.name} (${unit.symbol})
Expression: ${unit.expression}
SI Equivalent: ${unit.si_equivalent}
Shorthand: ${unit.shorthand}
Description: ${unit.description}
`;
  } else {
    return `Unit ${symbol} not found`;
  }
}

const derivedUnitsMap = {};

function createDerivedUnitsMap() {
  const db = new QMUDatabase();
  for (const [symbol, unit] of Object.entries(db.getAllUnits())) {
    if (unit.expression) {
      const baseUnits = unit.base_units;
      const expression = Object.entries(baseUnits)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([sym, pow]) => pow === 1 ? sym : `${sym}^${pow}`)
        .join('*');
      derivedUnitsMap[expression] = unit;
    }
  }

  console.log("\nDebug: Derived units map:");
  for (const [expr, unit] of Object.entries(derivedUnitsMap)) {
    console.log(`${expr}: ${unit.symbol}`);
  }
}

function simplifyAndMatchUnit(unitOrQuantity) {
  let baseUnits, value;
  if (unitOrQuantity instanceof QMUQuantity) {
    baseUnits = unitOrQuantity.unit.base_units;
    value = unitOrQuantity.value;
  } else if (unitOrQuantity instanceof QMUUnit) {
    baseUnits = unitOrQuantity.base_units;
    value = 1;
  } else {
    throw new TypeError(`Expected QMUQuantity or QMUUnit, got ${typeof unitOrQuantity}`);
  }

  const simplifiedExpression = Object.entries(baseUnits)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([sym, pow]) => pow === 1 ? sym : `${sym}^${pow}`)
    .join('*')
    .replace(/\^1(?!\d)/g, '');

  console.log(`Debug: Simplified expression: ${simplifiedExpression}`);

  const matchedUnit = derivedUnitsMap[simplifiedExpression];
  if (matchedUnit) {
    console.log(`Debug: Matched unit: ${matchedUnit.symbol}`);
    return new QMUQuantity(value, matchedUnit);
  } else {
    console.log(`Debug: No match found, creating custom unit`);
    const customUnit = new QMUUnit("Custom Unit", simplifiedExpression, simplifiedExpression);
    return new QMUQuantity(value, customUnit);
  }
}

// Initialize the derived units map
createDerivedUnitsMap();

module.exports = {
  QMUUnit,
  QMUQuantity,
  QMUDatabase,
  getUnitInfo,
  simplifyAndMatchUnit
};