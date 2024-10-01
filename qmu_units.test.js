const { QMUUnit, QMUDatabase } = require('./qmu_units');
const fs = require('fs');
const path = require('path');

// Mock fs.existsSync and fs.readFileSync for testing
jest.mock('fs');

describe('QMUUnit', () => {
  test('creates a basic unit correctly', () => {
    const unit = new QMUUnit('Electron mass', 'me');
    expect(unit.name).toBe('Electron mass');
    expect(unit.symbol).toBe('me');
    expect(unit.base_units).toEqual({ me: 1 });
  });

  test('parses a derived unit expression correctly', () => {
    const unit = new QMUUnit('Light', 'ligt', 'me * λC^3 * Fq^3');
    expect(unit.base_units).toEqual({ me: 1, 'λC': 3, Fq: 3 });
  });

  test('loads description correctly when file exists', () => {
    fs.existsSync.mockReturnValue(true);
    fs.readFileSync.mockReturnValue(`
# Unit: Test Unit

## Description
This is a test description.

## Other Information
Some other information.
    `);

    const unit = new QMUUnit('Test Unit', 'test');
    expect(unit.description).toBe('This is a test description.');
  });

  test('returns default message when description file does not exist', () => {
    fs.existsSync.mockReturnValue(false);

    const unit = new QMUUnit('Test Unit', 'test');
    expect(unit.description).toBe('No description available.');
  });
});

describe('QMUDatabase', () => {
  let db;

  beforeAll(() => {
    // Mock JSON data
    fs.readFileSync.mockReturnValueOnce(JSON.stringify({
      base_units: {
        me: { name: 'Electron mass', symbol: 'me', si_equivalent: '9.1093837015e-31 kg' }
      },
      derived_units: {
        ligt: { name: 'Light', symbol: 'ligt', expression: 'me * λC^3 * Fq^3' }
      }
    }));

    // Mock description files
    fs.existsSync.mockReturnValue(true);
    fs.readFileSync.mockReturnValue(`
# Unit: Test Unit

## Description
This is a test description.

## Other Information
Some other information.
    `);

    db = new QMUDatabase();
  });

  test('loads base units correctly', () => {
    const me = db.getUnit('me');
    expect(me).toBeInstanceOf(QMUUnit);
    expect(me.name).toBe('Electron mass');
    expect(me.si_equivalent).toBe('9.1093837015e-31 kg');
  });

  test('loads derived units correctly', () => {
    const ligt = db.getUnit('ligt');
    expect(ligt).toBeInstanceOf(QMUUnit);
    expect(ligt.name).toBe('Light');
    expect(ligt.expression).toBe('me * λC^3 * Fq^3');
  });

  test('returns all units', () => {
    const allUnits = db.getAllUnits();
    expect(Object.keys(allUnits).length).toBeGreaterThan(0);
    expect(allUnits['me']).toBeInstanceOf(QMUUnit);
    expect(allUnits['ligt']).toBeInstanceOf(QMUUnit);
  });

  test('loads unit descriptions', () => {
    const me = db.getUnit('me');
    expect(me.description).toBe('This is a test description.');

    const ligt = db.getUnit('ligt');
    expect(ligt.description).toBe('This is a test description.');
  });
});