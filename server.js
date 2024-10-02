const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
const { QMUDatabase, QMUUnit, QMUQuantity } = require('./qmu_units');

const app = express();
const port = 3000;

app.use(bodyParser.json());
app.use(express.static('public'));

const db = new QMUDatabase();

app.post('/solve', (req, res) => {
  console.log('Received solve request:', req.body);
  const { equation } = req.body;
  if (!equation) {
    console.error('No equation provided in request');
    return res.status(400).json({ error: 'No equation provided' });
  }
  try {
    const result = solveEquation(equation, db);
    console.log('Equation solved:', result);
    res.json({ result });
  } catch (error) {
    console.error('Error solving equation:', error);
    res.status(400).json({ error: error.message });
  }
});

function solveEquation(equation, db) {
  const parts = equation.replace(/\s+/g, '').split(/([+\-*/=])/);
  let result = null;
  let operation = null;

  for (let part of parts) {
    if (part === '=') break;
    if (part === '*' || part === '/' || part === '+' || part === '-') {
      operation = part;
    } else if (part.trim() !== '') {
      const match = part.match(/(-?\d*\.?\d+)?(\D+)/);
      if (!match) {
        throw new Error(`Invalid part in equation: ${part}`);
      }
      const [_, value, unitSymbol] = match;
      const unit = db.getUnit(unitSymbol);
      if (!unit) {
        throw new Error(`Unknown unit: ${unitSymbol}`);
      }

      const numericValue = value ? parseFloat(value) : 1;
      const currentQuantity = new QMUQuantity(numericValue, unit);

      if (result === null) {
        result = currentQuantity;
      } else {
        switch (operation) {
          case '*':
            result = result.multiply(currentQuantity);
            break;
          case '/':
            result = result.divide(currentQuantity);
            break;
          case '+':
            result = result.add(currentQuantity);
            break;
          case '-':
            result = result.subtract(currentQuantity);
            break;
          default:
            throw new Error(`Invalid operation: ${operation}`);
        }
      }
    }
  }

  if (!result) {
    throw new Error('Invalid equation');
  }

  return `${result.value} ${result.unit.symbol}`;
}

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});