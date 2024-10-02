class EquationParser {
    constructor(qmuDatabase) {
        this.qmuDatabase = qmuDatabase;
    }

    parse(equation) {
        const tokens = this.tokenize(equation);
        return this.parseExpression(tokens);
    }

    tokenize(equation) {
        return equation.match(/\d+(?:\.\d+)?|\w+|[+\-*/()]/g) || [];
    }

    parseExpression(tokens) {
        let result = this.parseTerm(tokens);
        while (tokens.length > 0 && (tokens[0] === '+' || tokens[0] === '-')) {
            const operator = tokens.shift();
            const term = this.parseTerm(tokens);
            if (operator === '+') {
                result = result.add(term);
            } else {
                result = result.subtract(term);
            }
        }
        return result;
    }

    parseTerm(tokens) {
        let result = this.parseFactor(tokens);
        while (tokens.length > 0 && (tokens[0] === '*' || tokens[0] === '/')) {
            const operator = tokens.shift();
            const factor = this.parseFactor(tokens);
            if (operator === '*') {
                result = result.multiply(factor);
            } else {
                result = result.divide(factor);
            }
        }
        return result;
    }

    parseFactor(tokens) {
        if (tokens[0] === '(') {
            tokens.shift();
            const result = this.parseExpression(tokens);
            if (tokens.shift() !== ')') {
                throw new Error("Mismatched parentheses");
            }
            return result;
        } else {
            const token = tokens.shift();
            if (/^\d+(?:\.\d+)?$/.test(token)) {
                return new QMUUnit("Number", token, null, null, parseFloat(token));
            } else {
                const unit = this.qmuDatabase.getUnit(token);
                if (!unit) {
                    throw new Error(`Unknown unit: ${token}`);
                }
                return unit;
            }
        }
    }
}