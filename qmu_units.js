const fs = require('fs');

class QMUUnit {
  constructor(name, symbol, expression = null, si_equivalent = null) {
    this.name = name;
    this.symbol = symbol;
    this.expression = expression;
    this.si_equivalent = si_equivalent;
    this.base_units = this.parseExpression();
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
}

class QMUDatabase {
  constructor() {
    this.units = {};
    this.loadUnits();
  }

  loadUnits() {
    const data = JSON.parse(fs.readFileSync('qmu_units_data.json', 'utf8'));
    
    for (const [symbol, unit] of Object.entries(data.base_units)) {
      this.units[symbol] = new QMUUnit(unit.name, symbol, null, unit.si_equivalent);
    }

    for (const [symbol, unit] of Object.entries(data.derived_units)) {
      this.units[symbol] = new QMUUnit(unit.name, symbol, unit.expression, unit.si_equivalent);
    }
  }

  getUnit(symbol) {
    return this.units[symbol];
  }

  getAllUnits() {
    return this.units;
  }
}

module.exports = { QMUUnit, QMUDatabase };