const code = `打印（"Hello World"）；

变量 名字 ＝ "世界"；
打印（"你好，" ＋ 名字 ＋ "！"）；

函数 问候（姓名）｛
  返回 "你好，" ＋ 姓名 ＋ "！"；
｝

打印（问候（"鸣言"））；

变量 数字列表 ＝ ［1，2，3，4，5］；
变量 平方列表 ＝ 映射（函数（x）｛ 返回 x × x ；｝，数字列表）；
打印（"平方列表：" ＋ 转字符串（平方列表））；`;

class MingyanInterpreter {
  constructor() {
    this.globalEnv = {};
    this.output = [];
    this.setupBuiltins();
  }

  setupBuiltins() {
    this.globalEnv['打印'] = (...args) => {
      this.output.push(args.map(this.formatValue).join(' '));
      return null;
    };
    this.globalEnv['真'] = true;
    this.globalEnv['假'] = false;
    this.globalEnv['映射'] = (fn, arr) => {
      return arr.map(fn);
    };
    this.globalEnv['空'] = null;
  }

  formatValue(val) {
    if (val === null) return '空';
    if (val === true) return '真';
    if (val === false) return '假';
    if (Array.isArray(val)) return `[${val.map(this.formatValue).join(', ')}]`;
    if (typeof val === 'object') {
      return `{${Object.entries(val).map(([k, v]) => 
        `${k}: ${this.formatValue(v)}`
      ).join(', ')}}`;
    }
    return String(val);
  }

  tokenize(code) {
    const tokens = [];
    const keywords = ['变量', '常量', '如果', '否则', '否则如果', '当', '遍历', '在',
      '函数', '返回', '类', '继承', '这个', '新', '尝试', '捕获', '最终',
      '抛出', '中断', '继续', '导入', '从', '作为', '是', '属于', '真', '假', '空',
      '且', '或', '非', '反转', '排序'];
    let i = 0;
    let line = 1;

    while (i < code.length) {
      if (code[i] === '\n') {
        line++;
        i++;
        continue;
      }
      if (/\s/.test(code[i])) {
        i++;
        continue;
      }
      if (code[i] === '#') {
        while (i < code.length && code[i] !== '\n') i++;
        continue;
      }
      if (/[a-zA-Z\u4e00-\u9fa5]/.test(code[i])) {
        let word = '';
        while (i < code.length && /[a-zA-Z0-9_\u4e00-\u9fa5]/.test(code[i])) {
          word += code[i];
          i++;
        }
        if (keywords.includes(word)) {
          tokens.push({ type: 'keyword', value: word, line });
        } else {
          tokens.push({ type: 'identifier', value: word, line });
        }
        continue;
      }
      if (/[0-9]/.test(code[i])) {
        let num = '';
        while (i < code.length && /[0-9.]/.test(code[i])) {
          num += code[i];
          i++;
        }
        tokens.push({ type: 'number', value: num, line });
        continue;
      }
      if (code[i] === '"' || code[i] === "'") {
        const quote = code[i];
        let str = '';
        i++;
        while (i < code.length && code[i] !== quote) {
          if (code[i] === '\\' && i + 1 < code.length) {
            i++;
            if (code[i] === 'n') str += '\n';
            else if (code[i] === 't') str += '\t';
            else str += code[i];
          } else {
            str += code[i];
          }
          i++;
        }
        i++;
        tokens.push({ type: 'string', value: str, line });
        continue;
      }
      if (code[i] === '=' && code[i + 1] === '=') {
        tokens.push({ type: 'operator', value: '==', line });
        i += 2;
        continue;
      }
      if (code[i] === '!' && code[i + 1] === '=') {
        tokens.push({ type: 'operator', value: '!=', line });
        i += 2;
        continue;
      }
      if (code[i] === '<' && code[i + 1] === '=') {
        tokens.push({ type: 'operator', value: '<=', line });
        i += 2;
        continue;
      }
      if (code[i] === '>' && code[i + 1] === '=') {
        tokens.push({ type: 'operator', value: '>=', line });
        i += 2;
        continue;
      }
      // 支持中文运算符
      const chineseOperatorMap = {
        '＋': '+', '－': '-', '×': '*', '÷': '/', '％': '%',
        '＝': '=', '＜': '<', '＞': '>', '≤': '<=', '≥': '>='
      };
      
      if (chineseOperatorMap[code[i]]) {
        tokens.push({ type: 'operator', value: chineseOperatorMap[code[i]], line });
        i++;
        continue;
      }
      if ('+-*/%=<>!?:'.includes(code[i])) {
        tokens.push({ type: 'operator', value: code[i], line });
        i++;
        continue;
      }
      // 支持中文符号（自动转换为对应的英文符号）
      const chinesePunctuationMap = {
        '（': '(', '）': ')',
        '｛': '{', '｝': '}',
        '［': '[', '］': ']',
        '；': ';',
        '，': ',',
        '：': ':',
        '＝': '='
      };
      
      if (chinesePunctuationMap[code[i]]) {
        tokens.push({ type: 'punctuation', value: chinesePunctuationMap[code[i]], line });
        i++;
        continue;
      }
      if ('{}[](),;:.'.includes(code[i])) {
        tokens.push({ type: 'punctuation', value: code[i], line });
        i++;
        continue;
      }
      i++;
    }
    return tokens;
  }

  parse(tokens) {
    let index = 0;

    const peek = () => tokens[index];
    const consume = () => tokens[index++];
    const expect = (type, value) => {
      const token = consume();
      if (!token) {
        throw new Error(`第 ${index > 0 ? tokens[index - 1]?.line || 0 : 0} 行: 意外的文件结束`);
      }
      if (token.type !== type || (value && token.value !== value)) {
        throw new Error(`第 ${token.line} 行: 期望 ${value || type}，得到 ${token.value}`);
      }
      return token;
    };

    const parseExpression = () => parseLogicalOr();

    const parseLogicalOr = () => {
      let left = parseLogicalAnd();
      while (peek()?.value === '或') {
        consume();
        const right = parseLogicalAnd();
        left = { type: 'BinaryOp', op: '或', left, right };
      }
      return left;
    };

    const parseLogicalAnd = () => {
      let left = parseComparison();
      while (peek()?.value === '且') {
        consume();
        const right = parseComparison();
        left = { type: 'BinaryOp', op: '且', left, right };
      }
      return left;
    };

    const parseComparison = () => {
      let left = parseAdditive();
      while (['==', '!=', '<', '>', '<=', '>='].includes(peek()?.value || '')) {
        const op = consume().value;
        const right = parseAdditive();
        left = { type: 'BinaryOp', op, left, right };
      }
      return left;
    };

    const parseAdditive = () => {
      let left = parseMultiplicative();
      while (['+', '-'].includes(peek()?.value || '')) {
        const op = consume().value;
        const right = parseMultiplicative();
        left = { type: 'BinaryOp', op, left, right };
      }
      return left;
    };

    const parseMultiplicative = () => {
      let left = parseUnary();
      while (['*', '/', '%'].includes(peek()?.value || '')) {
        const op = consume().value;
        const right = parseUnary();
        left = { type: 'BinaryOp', op, left, right };
      }
      return left;
    };

    const parseUnary = () => {
      if (peek()?.value === '非' || peek()?.value === '!' || peek()?.value === '-') {
        const op = consume().value;
        const operand = parseUnary();
        return { type: 'UnaryOp', op, operand };
      }
      return parsePrimary();
    };

    const parsePrimary = () => {
      const token = peek();
      if (token?.type === 'number') {
        const val = consume().value;
        return val.includes('.') ? parseFloat(val) : parseInt(val, 10);
      }
      if (token?.type === 'string') {
        return consume().value;
      }
      if (token?.value === '真') {
        consume();
        return true;
      }
      if (token?.value === '假') {
        consume();
        return false;
      }
      if (token?.value === '空') {
        consume();
        return null;
      }
      if (token?.value === '(') {
        consume();
        const expr = parseExpression();
        expect('punctuation', ')');
        return expr;
      }
      if (token?.value === '[') {
        consume();
        const elements = [];
        if (peek()?.value !== ']') {
          elements.push(parseExpression());
          while (peek()?.value === ',') {
            consume();
            elements.push(parseExpression());
          }
        }
        expect('punctuation', ']');
        return elements;
      }
      if (token?.value === '函数') {
        consume();
        expect('punctuation', '(');
        const params = [];
        if (peek()?.type === 'identifier') {
          params.push(consume().value);
          while (peek()?.value === ',') {
            consume();
            params.push(consume().value);
          }
        }
        expect('punctuation', ')');
        expect('punctuation', '{');
        const body = parseBlock();
        expect('punctuation', '}');
        return { type: 'Function', params, body };
      }
      if (token?.type === 'identifier') {
        const name = consume().value;
        if (peek()?.value === '(') {
          consume();
          const args = [];
          if (peek()?.value !== ')') {
            args.push(parseExpression());
            while (peek()?.value === ',') {
              consume();
              args.push(parseExpression());
            }
          }
          expect('punctuation', ')');
          return { type: 'Call', name, args };
        }
        if (peek()?.value === '[') {
          consume();
          const index = parseExpression();
          expect('punctuation', ']');
          return { type: 'Index', name, index };
        }
        return { type: 'Variable', name };
      }
      throw new Error(`第 ${token?.line || 0} 行: 未知表达式`);
    };

    const parseStatement = () => {
      const token = peek();
      if (token?.value === '变量' || token?.value === '常量') {
        const isConst = consume().value === '常量';
        const name = expect('identifier').value;
        expect('operator', '=');
        const value = parseExpression();
        expect('punctuation', ';');
        return { type: 'VarDecl', name, value, isConst };
      }
      if (token?.type === 'identifier') {
        const name = consume().value;
        if (peek()?.value === '(') {
          consume();
          const args = [];
          if (peek()?.value !== ')') {
            args.push(parseExpression());
            while (peek()?.value === ',') {
              consume();
              args.push(parseExpression());
            }
          }
          expect('punctuation', ')');
          expect('punctuation', ';');
          return { type: 'Expression', expr: { type: 'Call', name, args } };
        }
        if (['=', '+=', '-=', '*=', '/='].includes(peek()?.value || '')) {
          const op = consume().value;
          const value = parseExpression();
          expect('punctuation', ';');
          return { type: 'Assignment', name, op, value };
        }
        expect('punctuation', ';');
        return { type: 'Expression', expr: { type: 'Variable', name } };
      }
      if (token?.value === '如果') {
        consume();
        expect('punctuation', '(');
        const condition = parseExpression();
        expect('punctuation', ')');
        expect('punctuation', '{');
        const body = parseBlock();
        expect('punctuation', '}');
        const elifClauses = [];
        while (peek()?.value === '否则如果') {
          consume();
          expect('punctuation', '(');
          const cond = parseExpression();
          expect('punctuation', ')');
          expect('punctuation', '{');
          const elifBody = parseBlock();
          expect('punctuation', '}');
          elifClauses.push({ condition: cond, body: elifBody });
        }
        let elseBody = null;
        if (peek()?.value === '否则') {
          consume();
          expect('punctuation', '{');
          elseBody = parseBlock();
          expect('punctuation', '}');
        }
        return { type: 'If', condition, body, elifClauses, elseBody };
      }
      if (token?.value === '当') {
        consume();
        expect('punctuation', '(');
        const condition = parseExpression();
        expect('punctuation', ')');
        expect('punctuation', '{');
        const body = parseBlock();
        expect('punctuation', '}');
        return { type: 'While', condition, body };
      }
      if (token?.value === '遍历') {
        consume();
        const varName = expect('identifier').value;
        expect('keyword', '在');
        const iterable = parseExpression();
        expect('punctuation', '{');
        const body = parseBlock();
        expect('punctuation', '}');
        return { type: 'For', varName, iterable, body };
      }
      if (token?.value === '函数') {
        consume();
        const name = expect('identifier').value;
        expect('punctuation', '(');
        const params = [];
        if (peek()?.type === 'identifier') {
          params.push(consume().value);
          while (peek()?.value === ',') {
            consume();
            params.push(consume().value);
          }
        }
        expect('punctuation', ')');
        expect('punctuation', '{');
        const body = parseBlock();
        expect('punctuation', '}');
        return { type: 'FuncDecl', name, params, body };
      }
      if (token?.value === '返回') {
        consume();
        let value = null;
        if (peek()?.value !== ';') {
          value = parseExpression();
        }
        expect('punctuation', ';');
        return { type: 'Return', value };
      }
      if (token?.value === '中断') {
        consume();
        expect('punctuation', ';');
        return { type: 'Break' };
      }
      if (token?.value === '继续') {
        consume();
        expect('punctuation', ';');
        return { type: 'Continue' };
      }
      throw new Error(`第 ${token?.line || 0} 行: 未知语句`);
    };

    const parseBlock = () => {
      const statements = [];
      while (peek() && peek()?.value !== '}') {
        statements.push(parseStatement());
      }
      if (!peek()) {
        throw new Error(`第 ${tokens[tokens.length - 1]?.line || 0} 行: 缺少闭合的 '}'`);
      }
      return statements;
    };

    const program = [];
    while (index < tokens.length) {
      program.push(parseStatement());
    }
    return program;
  }

  evaluate(expr, env) {
    if (expr === undefined) return undefined;
    if (typeof expr === 'number' || typeof expr === 'string' || 
        typeof expr === 'boolean' || expr === null || Array.isArray(expr)) {
      return expr;
    }
    if (typeof expr === 'object' && expr) {
      switch (expr.type) {
        case 'Variable':
          if (!(expr.name in env)) {
            throw new Error(`未定义的变量: ${expr.name}`);
          }
          return env[expr.name];
        case 'Call': {
          const fn = this.evaluate({ type: 'Variable', name: expr.name }, env);
          if (typeof fn !== 'function') {
            throw new Error(`${expr.name} 不是函数`);
          }
          const args = expr.args.map((a) => this.evaluate(a, env));
          return fn(...args);
        }
        case 'BinaryOp': {
          const left = this.evaluate(expr.left, env);
          const right = this.evaluate(expr.right, env);
          switch (expr.op) {
            case '+': return (Number(left) || left) + (Number(right) || right);
            case '-': return Number(left) - Number(right);
            case '*': return Number(left) * Number(right);
            case '/': return Number(left) / Number(right);
            case '%': return Number(left) % Number(right);
            case '==': return left == right;
            case '!=': return left != right;
            case '<': return Number(left) < Number(right);
            case '>': return Number(left) > Number(right);
            case '<=': return Number(left) <= Number(right);
            case '>=': return Number(left) >= Number(right);
            case '且': return Boolean(left) && Boolean(right);
            case '或': return Boolean(left) || Boolean(right);
            default: throw new Error(`未知运算符: ${expr.op}`);
          }
        }
        case 'UnaryOp': {
          const operand = this.evaluate(expr.operand, env);
          switch (expr.op) {
            case '-': return -Number(operand);
            case '非':
            case '!': return !Boolean(operand);
            default: throw new Error(`未知一元运算符: ${expr.op}`);
          }
        }
        case 'Function': {
          return (...args) => {
            const newEnv = { ...env };
            expr.params.forEach((param, i) => {
              newEnv[param] = args[i];
            });
            for (const stmt of expr.body) {
              const r = this.execute(stmt, newEnv);
              if (r === 'return') {
                return newEnv['_returnValue'];
              }
            }
            return null;
          };
        }
        case 'Index': {
          const obj = this.evaluate({ type: 'Variable', name: expr.name }, env);
          const idx = this.evaluate(expr.index, env);
          if (Array.isArray(obj) || typeof obj === 'string') {
            return obj[idx];
          }
          throw new Error(`无法索引: ${typeof obj}`);
        }
      }
    }
    return expr;
  }

  execute(stmt, env) {
    if (!stmt) return;
    if (typeof stmt === 'object' && stmt.type) {
      switch (stmt.type) {
        case 'VarDecl': {
          const value = this.evaluate(stmt.value, env);
          env[stmt.name] = value;
          return value;
        }
        case 'Assignment': {
          const value = this.evaluate(stmt.value, env);
          switch (stmt.op) {
            case '=': env[stmt.name] = value; break;
            case '+=': env[stmt.name] = (Number(env[stmt.name]) || 0) + (Number(value) || 0); break;
            case '-=': env[stmt.name] = Number(env[stmt.name]) - Number(value); break;
            case '*=': env[stmt.name] = Number(env[stmt.name]) * Number(value); break;
            case '/=': env[stmt.name] = Number(env[stmt.name]) / Number(value); break;
          }
          return env[stmt.name];
        }
        case 'Expression': {
          return this.evaluate(stmt.expr, env);
        }
        case 'If': {
          if (Boolean(this.evaluate(stmt.condition, env))) {
            for (const s of stmt.body) {
              const result = this.execute(s, env);
              if (result === 'return') return result;
            }
          } else {
            for (const elif of stmt.elifClauses) {
              if (Boolean(this.evaluate(elif.condition, env))) {
                for (const s of elif.body) {
                  const result = this.execute(s, env);
                  if (result === 'return') return result;
                }
                return;
              }
            }
            if (stmt.elseBody) {
              for (const s of stmt.elseBody) {
                const result = this.execute(s, env);
                if (result === 'return') return result;
              }
            }
          }
          return;
        }
        case 'While': {
          while (Boolean(this.evaluate(stmt.condition, env))) {
            for (const s of stmt.body) {
              const result = this.execute(s, env);
              if (result === 'break') return;
              if (result === 'continue') break;
              if (result === 'return') return result;
            }
          }
          return;
        }
        case 'For': {
          const iterable = this.evaluate(stmt.iterable, env);
          if (!Array.isArray(iterable)) {
            throw new Error('遍历需要列表');
          }
          for (const item of iterable) {
            env[stmt.varName] = item;
            for (const s of stmt.body) {
              const result = this.execute(s, env);
              if (result === 'break') return;
              if (result === 'continue') break;
              if (result === 'return') return result;
            }
          }
          return;
        }
        case 'FuncDecl': {
          env[stmt.name] = (...args) => {
            const newEnv = { ...env };
            stmt.params.forEach((param, i) => {
              newEnv[param] = args[i];
            });
            for (const s of stmt.body) {
              const r = this.execute(s, newEnv);
              if (r === 'return') {
                return newEnv['_returnValue'];
              }
            }
            return null;
          };
          return;
        }
        case 'Return': {
          const value = stmt.value ? this.evaluate(stmt.value, env) : null;
          env['_returnValue'] = value;
          return 'return';
        }
        case 'Break': {
          return 'break';
        }
        case 'Continue': {
          return 'continue';
        }
      }
    }
    return;
  }

  run(code) {
    this.output = [];
    try {
      const tokens = this.tokenize(code);
      console.log('Tokens:', JSON.stringify(tokens, null, 2));
      const program = this.parse(tokens);
      console.log('Program:', JSON.stringify(program, null, 2));
      const env = { ...this.globalEnv };
      for (const stmt of program) {
        if (!stmt) {
          throw new Error('内部错误: 解析产生了 undefined 语句');
        }
        this.execute(stmt, env);
      }
      return { output: this.output.join('\n'), error: '' };
    } catch (e) {
      return { output: this.output.join('\n'), error: String(e) };
    }
  }
}

const interpreter = new MingyanInterpreter();
const result = interpreter.run(code);
console.log('Result:', result);
