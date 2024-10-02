const fs = require('fs');
const path = require('path');

class QMUUnit {
    constructor(name, symbol, expression = null, si_equivalent = null) {
        console.log('QMUUnit constructor called with:');
        console.log(`name: ${name}`);
        console.log(`symbol: ${symbol}`);
        console.log(`expression: ${expression}`);
        console.log(`si_equivalent: ${si_equivalent}`);

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

    add(other, value1, value2) {
        if (JSON.stringify(this.base_units) !== JSON.stringify(other.base_units)) {
            throw new Error("Cannot add units with different base units");
        }
        return new QMUUnit(this.name, this.symbol, this.expression, this.si_equivalent);
    }

    subtract(other, value1, value2) {
        if (JSON.stringify(this.base_units) !== JSON.stringify(other.base_units)) {
            throw new Error("Cannot subtract units with different base units");
        }
        return new QMUUnit(this.name, this.symbol, this.expression, this.si_equivalent);
    }

    multiply(other) {
        const newBaseUnits = {};
        for (const [unit, power] of Object.entries(this.base_units)) {
            newBaseUnits[unit] = (newBaseUnits[unit] || 0) + power;
        }
        for (const [unit, power] of Object.entries(other.base_units)) {
            newBaseUnits[unit] = (newBaseUnits[unit] || 0) + power;
        }
        const newExpression = `(${this.expression || this.symbol}) * (${other.expression || other.symbol})`;
        return new QMUUnit("Custom Unit", newExpression, newExpression, null);
    }

    divide(other) {
        const newBaseUnits = {};
        for (const [unit, power] of Object.entries(this.base_units)) {
            newBaseUnits[unit] = (newBaseUnits[unit] || 0) + power;
        }
        for (const [unit, power] of Object.entries(other.base_units)) {
            newBaseUnits[unit] = (newBaseUnits[unit] || 0) - power;
        }
        const newExpression = `(${this.expression || this.symbol}) / (${other.expression || other.symbol})`;
        return new QMUUnit("Custom Unit", newExpression, newExpression, null);
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
        console.log('QMUDatabase constructor called');
        this.units = {};
        this.loadUnits();
    }

    loadUnits() {
        console.log('loadUnits method called');
        try {
            const data = JSON.parse(fs.readFileSync(path.join(__dirname, 'qmu_units_data.json'), 'utf8'));
            console.log('qmu_units_data.json loaded successfully');

            console.log('Loading base units...');
            for (const [symbol, unit] of Object.entries(data.base_units)) {
                console.log(`Creating base unit: ${symbol}`);
                this.units[symbol] = new QMUUnit(unit.name, symbol, null, unit.si_equivalent);
            }

            console.log('Loading derived units...');
            for (const [symbol, unit] of Object.entries(data.derived_units)) {
                console.log(`Creating derived unit: ${symbol}`);
                this.units[symbol] = new QMUUnit(unit.name, symbol, unit.expression, unit.si_equivalent);
            }

            console.log('Loading measurement units...');
            for (const [symbol, unit] of Object.entries(data.measurement_units)) {
                console.log(`Creating measurement unit: ${symbol}`);
                this.units[symbol] = new QMUUnit(unit.name, symbol, unit.expression, null);
            }

            console.log('Finished loading units.');
        } catch (error) {
            console.error('Error in loadUnits:', error);
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
        const data = JSON.parse(fs.readFileSync(path.join(__dirname, 'qmu_units_data.json'), 'utf8'));
        return Object.fromEntries(
            Object.entries(this.units).filter(([symbol, unit]) => unit.expression && !data.measurement_units[symbol])
        );
    }

    getMeasurementUnits() {
        const data = JSON.parse(fs.readFileSync(path.join(__dirname, 'qmu_units_data.json'), 'utf8'));
        return Object.fromEntries(
            Object.entries(this.units).filter(([symbol, _]) => data.measurement_units[symbol])
        );
    }
}

module.exports = { QMUUnit, QMUDatabase };