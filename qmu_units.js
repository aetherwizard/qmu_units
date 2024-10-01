const fs = require('fs');
const path = require('path');

class QMUUnit {
  constructor(name, symbol, expression = null, si_equivalent = null) {
    this.name = name;
    this.symbol = symbol;
    this.expression = expression;
    this.si_equivalent = si_equivalent;
    this.base_units = this.parseExpression();
    this.description = this.loadDescription();
  }

  parseExpression() {
    if (!this.expression) {
      return { [this.symbol]: 1 };
    }

    const base_units = {};
    const parts = this.expression.split(/([*/])/);
    let current_op = '*';

    for (let part of parts) {
      part = part.trim();
      if (part === '*' || part === '/') {
        current_op = part;
        continue;
      }

      const [unit, power] = part.split('^');
      const powerValue = power ? parseInt(power) : 1;

      if (current_op === '*') {
        base_units[unit] = (base_units[unit] || 0) + powerValue;
      } else {
        base_units[unit] = (base_units[unit] || 0) - powerValue;
      }
    }

    return Object.fromEntries(
      Object.entries(base_units).filter(([_, value]) => value !== 0)
    );
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
      this.units[symbol] = new QMUUnit(unit.name, symbol, unit.expression, unit.si_equivalent, unit.shorthand);
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

  getBaseUnits() {
    return Object.fromEntries(
      Object.entries(this.units).filter(([_, unit]) => !unit.expression)
    );
  }

  getDerivedUnits() {
    return Object.fromEntries(
      Object.entries(this.units).filter(([_, unit]) => unit.expression && !data.measurement_units[unit.symbol])
    );
  }

  getMeasurementUnits() {
    return Object.fromEntries(
      Object.entries(this.units).filter(([symbol, _]) => data.measurement_units[symbol])
    );
  }
}
module.exports = { QMUUnit, QMUDatabase };