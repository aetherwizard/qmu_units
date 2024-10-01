{
    "scripts": {
      "test": "jest",
      "test:watch": "jest --watch"
    }
  // Additional tests in qmu_units.test.js

describe('QMUUnit advanced functionality', () => {
    test('parses complex expressions correctly', () => {
      const unit = new QMUUnit('Complex Unit', 'cpx', 'me^2 * λC^-1 * Fq^0.5 / eemax');
      expect(unit.baseUnits).toEqual({ 'me': 2, 'λC': -1, 'Fq': 0.5, 'eemax': -1 });
    });
  
    test('handles SI equivalent correctly', () => {
      const unit = new QMUUnit('Inductance', 'indc', 'me * λC^2 / eemax^2', '3.8314755224e-17 henry');
      expect(unit.siEquivalent).toBe('3.8314755224e-17 henry');
    });
  
    test('loads description correctly', () => {
      const unit = new QMUUnit('Test Unit', 'test');
      // This test will need to be adjusted based on how you implement loadDescription in JS
      expect(unit.description).toBe("Description placeholder");
    });
  });}