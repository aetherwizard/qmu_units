const { QMUUnit, QMUDatabase } = require('./qmu_units');

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
});

describe('QMUDatabase', () => {
  let db;

  beforeAll(() => {
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
});