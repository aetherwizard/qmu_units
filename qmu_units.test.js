// qmu_units.test.js

const QMUUnit = require('./qmu_units');

describe('QMUUnit', () => {
  test('creates a basic unit correctly', () => {
    const unit = new QMUUnit('Electron mass', 'me');
    expect(unit.name).toBe('Electron mass');
    expect(unit.symbol).toBe('me');
    expect(unit.expression).toBeNull();
    expect(unit.baseUnits).toEqual({ me: 1 });
  });

  test('creates a derived unit correctly', () => {
    const unit = new QMUUnit('Light', 'ligt', 'me * λC^3 * Fq^3');
    expect(unit.name).toBe('Light');
    expect(unit.symbol).toBe('ligt');
    expect(unit.expression).toBe('me * λC^3 * Fq^3');
    // Note: This expectation might need adjustment based on your actual implementation
    expect(unit.baseUnits).toEqual({ me: 1, 'λC': 3, 'Fq': 3 });
  });
});