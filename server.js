const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const { QMUDatabase } = require('./qmu_units');

const app = express();
const port = 3000;

app.use(bodyParser.json());
app.use(express.static('public'));

const db = new QMUDatabase();

function updateUnitData(oldSymbol, newData) {
  const dataPath = path.join(__dirname, 'qmu_units_data.json');
  let qmuData = JSON.parse(fs.readFileSync(dataPath, 'utf8'));

  let unitCategory = qmuData.base_units[oldSymbol] ? 'base_units' : 'derived_units';

  delete qmuData[unitCategory][oldSymbol];
  qmuData[unitCategory][newData.symbol] = {
    name: newData.name,
    symbol: newData.symbol,
    expression: newData.expression,
    si_equivalent: newData.si_equivalent,
    shorthand: newData.shorthand
  };

  fs.writeFileSync(dataPath, JSON.stringify(qmuData, null, 2));

  if (oldSymbol !== newData.symbol) {
    const oldPath = path.join(__dirname, 'unit_descriptions', `${oldSymbol}.txt`);
    const newPath = path.join(__dirname, 'unit_descriptions', `${newData.symbol}.txt`);
    fs.renameSync(oldPath, newPath);
  }

  // Update the description file content
  const descriptionPath = path.join(__dirname, 'unit_descriptions', `${newData.symbol}.txt`);
  const descriptionContent = `# Unit: ${newData.name}\n\n## Description\n${newData.description}\n`;
  fs.writeFileSync(descriptionPath, descriptionContent);

  // Reload the QMUDatabase to reflect changes
  db.loadUnits();
}

app.get('/api/units', (req, res) => {
  res.json(Object.values(db.getAllUnits()).map(unit => ({
    symbol: unit.symbol,
    name: unit.name
  })));
});

app.get('/api/unit/:symbol', (req, res) => {
  const unit = db.getUnit(req.params.symbol);
  if (unit) {
    res.json({
      symbol: unit.symbol,
      name: unit.name,
      description: unit.description,
      expression: unit.expression,
      si_equivalent: unit.si_equivalent,
      shorthand: unit.shorthand
    });
  } else {
    res.status(404).json({ error: 'Unit not found' });
  }
});

app.post('/api/unit/:symbol', (req, res) => {
  const oldSymbol = req.params.symbol;
  const newData = req.body;

  try {
    updateUnitData(oldSymbol, newData);
    res.json({ success: true, message: 'Unit updated successfully' });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Failed to update unit', error: error.message });
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});