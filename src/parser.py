from lexer import TokenType, KEYWORD_NAMES
from ast_nodes import *


class ParseError(Exception):
    def __init__(self, message, token=None):
        self.message = message
        self.token = token
        if token:
            super().__init__(f'语法错误 第{token.line}行 第{token.column}列: {message}')
        else:
            super().__init__(f'语法错误: {message}')


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def error(self, message):
        token = self.current()
        raise ParseError(message, token)

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def peek(self, offset=1):
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]

    def advance(self):
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def match(self, *types):
        if self.current().type in types:
            return self.advance()
        return None

    def expect(self, token_type, message=None):
        if self.current().type == token_type:
            return self.advance()
        if message is None:
            message = f'期望 {token_type.name}，但得到 {self.current().type.name}'
        self.error(message)

    def is_keyword(self, keyword_name):
        t = self.current()
        if t.type == TokenType.KEYWORD and t.value in KEYWORD_NAMES:
            return KEYWORD_NAMES[t.value] == keyword_name
        if t.type == TokenType.AND and keyword_name == 'AND':
            return True
        if t.type == TokenType.OR and keyword_name == 'OR':
            return True
        if t.type == TokenType.NOT and keyword_name == 'NOT':
            return True
        return False

    def match_keyword(self, keyword_name):
        if self.is_keyword(keyword_name):
            return self.advance()
        return None

    def skip_newlines(self):
        while self.current().type == TokenType.NEWLINE:
            self.advance()

    def expect_newline_or_semicolon(self):
        if self.current().type in (TokenType.NEWLINE, TokenType.EOF, TokenType.RBRACE):
            while self.current().type == TokenType.NEWLINE:
                self.advance()
            return
        if self.current().type == TokenType.SEMICOLON:
            self.advance()
            self.skip_newlines()
            return
        self.error('期望换行或分号')

    def parse(self):
        statements = []
        self.skip_newlines()
        while self.current().type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self.skip_newlines()
        return Program(statements)

    def parse_statement(self):
        self.skip_newlines()
        if self.current().type == TokenType.EOF:
            return None

        if self.is_keyword('VAR'):
            return self.parse_var_declaration(is_const=False)
        if self.is_keyword('CONST'):
            return self.parse_var_declaration(is_const=True)
        if self.is_keyword('IF'):
            return self.parse_if_statement()
        if self.is_keyword('WHILE'):
            return self.parse_while_statement()
        if self.is_keyword('FOR'):
            return self.parse_for_statement()
        if self.is_keyword('FUNC'):
            return self.parse_func_declaration()
        if self.is_keyword('RETURN'):
            return self.parse_return_statement()
        if self.is_keyword('BREAK'):
            self.advance()
            self.expect_newline_or_semicolon()
            return BreakStatement()
        if self.is_keyword('CONTINUE'):
            self.advance()
            self.expect_newline_or_semicolon()
            return ContinueStatement()
        if self.is_keyword('CLASS'):
            return self.parse_class_declaration()
        if self.is_keyword('TRY'):
            return self.parse_try_catch()
        if self.is_keyword('RAISE'):
            return self.parse_raise_statement()
        if self.is_keyword('IMPORT'):
            return self.parse_import_statement()
        if self.is_keyword('FROM'):
            return self.parse_from_import_statement()

        return self.parse_expression_statement()

    def parse_var_declaration(self, is_const=False):
        self.advance()
        name_token = self.expect(TokenType.IDENTIFIER, '期望变量名')
        name = name_token.value
        value = None
        if self.match(TokenType.ASSIGN):
            value = self.parse_expression()
        if value is None and not is_const:
            value = NullLiteral()
        if value is None:
            self.error('常量声明必须有初始值')
        self.expect_newline_or_semicolon()
        return VarDeclaration(name, value, is_const)

    def parse_block(self):
        self.expect(TokenType.LBRACE, '期望 "{"')
        self.skip_newlines()
        statements = []
        while self.current().type != TokenType.RBRACE and self.current().type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self.skip_newlines()
        self.expect(TokenType.RBRACE, '期望 "}"')
        return statements

    def parse_if_statement(self):
        self.advance()
        condition = self.parse_expression()
        self.skip_newlines()
        body = self.parse_block()
        self.skip_newlines()

        elif_clauses = []
        while self.is_keyword('ELIF'):
            self.advance()
            elif_cond = self.parse_expression()
            self.skip_newlines()
            elif_body = self.parse_block()
            elif_clauses.append((elif_cond, elif_body))
            self.skip_newlines()

        else_body = None
        if self.is_keyword('ELSE'):
            self.advance()
            self.skip_newlines()
            else_body = self.parse_block()
            self.skip_newlines()

        return IfStatement(condition, body, elif_clauses, else_body)

    def parse_while_statement(self):
        self.advance()
        condition = self.parse_expression()
        self.skip_newlines()
        body = self.parse_block()
        return WhileStatement(condition, body)

    def parse_for_statement(self):
        self.advance()
        var_token = self.expect(TokenType.IDENTIFIER, '期望循环变量名')
        var_name = var_token.value
        if not self.is_keyword('IN'):
            self.error('期望 "在" 关键字')
        self.advance()
        iterable = self.parse_expression()
        self.skip_newlines()
        body = self.parse_block()
        return ForStatement(var_name, iterable, body)

    def parse_func_declaration(self):
        self.advance()
        name_token = self.expect(TokenType.IDENTIFIER, '期望函数名')
        name = name_token.value
        self.expect(TokenType.LPAREN, '期望 "("')
        params = []
        defaults = []
        has_default = False
        while self.current().type != TokenType.RPAREN:
            if params:
                self.expect(TokenType.COMMA, '期望 ","')
            param_token = self.expect(TokenType.IDENTIFIER, '期望参数名')
            params.append(param_token.value)
            if self.match(TokenType.ASSIGN):
                default_val = self.parse_expression()
                defaults.append(default_val)
                has_default = True
            else:
                if has_default:
                    self.error('有默认值的参数后不能再有无默认值的参数')
                defaults.append(None)
        self.expect(TokenType.RPAREN, '期望 ")"')
        self.skip_newlines()
        body = self.parse_block()
        return FuncDeclaration(name, params, body, defaults)

    def parse_return_statement(self):
        self.advance()
        value = None
        if self.current().type not in (TokenType.NEWLINE, TokenType.SEMICOLON, TokenType.EOF, TokenType.RBRACE):
            value = self.parse_expression()
        self.expect_newline_or_semicolon()
        return ReturnStatement(value)

    def parse_class_declaration(self):
        self.advance()
        name_token = self.expect(TokenType.IDENTIFIER, '期望类名')
        name = name_token.value
        parent = None
        if self.is_keyword('EXTENDS'):
            self.advance()
            parent_token = self.expect(TokenType.IDENTIFIER, '期望父类名')
            parent = parent_token.value
        self.skip_newlines()
        body = self.parse_block()
        return ClassDeclaration(name, parent, body)

    def parse_try_catch(self):
        self.advance()
        self.skip_newlines()
        try_body = self.parse_block()
        self.skip_newlines()
        catch_var = None
        catch_body = None
        if self.is_keyword('CATCH'):
            self.advance()
            if self.current().type == TokenType.IDENTIFIER:
                catch_var = self.advance().value
            self.skip_newlines()
            catch_body = self.parse_block()
        finally_body = None
        if self.is_keyword('FINALLY'):
            self.advance()
            self.skip_newlines()
            finally_body = self.parse_block()
        return TryCatchStatement(try_body, catch_var, catch_body, finally_body)

    def parse_raise_statement(self):
        self.advance()
        value = self.parse_expression()
        self.expect_newline_or_semicolon()
        return RaiseStatement(value)

    def parse_import_statement(self):
        self.advance()
        module_token = self.expect(TokenType.IDENTIFIER, '期望模块名')
        module = module_token.value
        while self.current().type == TokenType.DOT:
            self.advance()
            part = self.expect(TokenType.IDENTIFIER, '期望模块名部分')
            module += '.' + part.value
        alias = None
        if self.is_keyword('AS'):
            self.advance()
            alias_token = self.expect(TokenType.IDENTIFIER, '期望别名')
            alias = alias_token.value
        self.expect_newline_or_semicolon()
        return ImportStatement(module, alias)

    def parse_from_import_statement(self):
        self.advance()
        module_token = self.expect(TokenType.IDENTIFIER, '期望模块名')
        module = module_token.value
        while self.current().type == TokenType.DOT:
            self.advance()
            part = self.expect(TokenType.IDENTIFIER, '期望模块名部分')
            module += '.' + part.value
        if not self.is_keyword('IMPORT'):
            self.error('期望 "导入" 关键字')
        self.advance()
        names = []
        name_token = self.expect(TokenType.IDENTIFIER, '期望导入名称')
        names.append(name_token.value)
        while self.match(TokenType.COMMA):
            name_token = self.expect(TokenType.IDENTIFIER, '期望导入名称')
            names.append(name_token.value)
        self.expect_newline_or_semicolon()
        return FromImportStatement(module, names)

    def parse_expression_statement(self):
        expr = self.parse_expression()
        if isinstance(expr, Identifier):
            if self.current().type == TokenType.ASSIGN:
                self.advance()
                value = self.parse_expression()
                self.expect_newline_or_semicolon()
                return Assignment(expr.name, value)
            if self.current().type in (TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN,
                                       TokenType.MULTIPLY_ASSIGN, TokenType.DIVIDE_ASSIGN):
                op_token = self.advance()
                value = self.parse_expression()
                self.expect_newline_or_semicolon()
                op_map = {
                    TokenType.PLUS_ASSIGN: '+',
                    TokenType.MINUS_ASSIGN: '-',
                    TokenType.MULTIPLY_ASSIGN: '*',
                    TokenType.DIVIDE_ASSIGN: '/',
                }
                return CompoundAssignment(expr.name, op_map[op_token.type], value)
        if isinstance(expr, IndexAccess):
            if self.current().type == TokenType.ASSIGN:
                self.advance()
                value = self.parse_expression()
                self.expect_newline_or_semicolon()
                return IndexAssignment(expr.obj, expr.index, value)
        if isinstance(expr, MemberAccess):
            if self.current().type == TokenType.ASSIGN:
                self.advance()
                value = self.parse_expression()
                self.expect_newline_or_semicolon()
                return MemberAssignment(expr.obj, expr.member, value)
        self.expect_newline_or_semicolon()
        return expr

    def parse_expression(self):
        return self.parse_ternary()

    def parse_ternary(self):
        expr = self.parse_or()
        if self.match(TokenType.QUESTION):
            true_expr = self.parse_expression()
            self.expect(TokenType.COLON, '期望 ":"')
            false_expr = self.parse_ternary()
            return TernaryExpression(expr, true_expr, false_expr)
        return expr

    def parse_or(self):
        left = self.parse_and()
        while self.is_keyword('OR') or self.current().type == TokenType.OR:
            self.advance()
            right = self.parse_and()
            left = BinaryOp('或', left, right)
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.is_keyword('AND') or self.current().type == TokenType.AND:
            self.advance()
            right = self.parse_not()
            left = BinaryOp('且', left, right)
        return left

    def parse_not(self):
        if self.is_keyword('NOT') or self.current().type == TokenType.NOT:
            self.advance()
            operand = self.parse_not()
            return UnaryOp('非', operand)
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_is()
        comp_ops = {
            TokenType.EQUAL: '==',
            TokenType.NOT_EQUAL: '!=',
            TokenType.LESS: '<',
            TokenType.GREATER: '>',
            TokenType.LESS_EQUAL: '<=',
            TokenType.GREATER_EQUAL: '>=',
        }
        while self.current().type in comp_ops:
            op = comp_ops[self.current().type]
            self.advance()
            right = self.parse_is()
            left = BinaryOp(op, left, right)
        return left

    def parse_is(self):
        left = self.parse_instanceof()
        if self.is_keyword('IS'):
            self.advance()
            right = self.parse_instanceof()
            return IsExpression(left, right)
        return left

    def parse_instanceof(self):
        left = self.parse_addition()
        if self.is_keyword('INSTANCEOF'):
            self.advance()
            class_token = self.expect(TokenType.IDENTIFIER, '期望类名')
            return InstanceofExpression(left, class_token.value)
        return left

    def parse_addition(self):
        left = self.parse_multiplication()
        while self.current().type in (TokenType.PLUS, TokenType.MINUS):
            op = '+' if self.current().type == TokenType.PLUS else '-'
            self.advance()
            right = self.parse_multiplication()
            left = BinaryOp(op, left, right)
        return left

    def parse_multiplication(self):
        left = self.parse_power()
        while self.current().type in (TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op_map = {TokenType.MULTIPLY: '*', TokenType.DIVIDE: '/', TokenType.MODULO: '%'}
            op = op_map[self.current().type]
            self.advance()
            right = self.parse_power()
            left = BinaryOp(op, left, right)
        return left

    def parse_power(self):
        left = self.parse_unary()
        if self.current().type == TokenType.POWER:
            self.advance()
            right = self.parse_unary()
            left = BinaryOp('**', left, right)
        return left

    def parse_unary(self):
        if self.current().type == TokenType.MINUS:
            self.advance()
            operand = self.parse_unary()
            return UnaryOp('-', operand)
        if self.current().type == TokenType.PLUS:
            self.advance()
            return self.parse_unary()
        return self.parse_postfix()

    def parse_postfix(self):
        expr = self.parse_primary()
        while True:
            if self.current().type == TokenType.LPAREN:
                self.advance()
                args = []
                while self.current().type != TokenType.RPAREN:
                    if args:
                        self.expect(TokenType.COMMA, '期望 ","')
                    args.append(self.parse_expression())
                self.expect(TokenType.RPAREN, '期望 ")"')
                expr = FuncCall(expr, args)
            elif self.current().type == TokenType.DOT:
                self.advance()
                member_token = self.expect(TokenType.IDENTIFIER, '期望成员名')
                member = member_token.value
                if self.current().type == TokenType.LPAREN:
                    self.advance()
                    args = []
                    while self.current().type != TokenType.RPAREN:
                        if args:
                            self.expect(TokenType.COMMA, '期望 ","')
                        args.append(self.parse_expression())
                    self.expect(TokenType.RPAREN, '期望 ")"')
                    expr = MethodCall(expr, member, args)
                else:
                    expr = MemberAccess(expr, member)
            elif self.current().type == TokenType.LBRACKET:
                self.advance()
                if self.current().type == TokenType.COLON:
                    start = None
                    self.advance()
                    end = None
                    step = None
                    if self.current().type != TokenType.RBRACKET and not (
                        self.current().type == TokenType.COLON
                    ):
                        end = self.parse_expression()
                    if self.current().type == TokenType.COLON:
                        self.advance()
                        if self.current().type != TokenType.RBRACKET:
                            step = self.parse_expression()
                    self.expect(TokenType.RBRACKET, '期望 "]"')
                    expr = SliceAccess(expr, start, end, step)
                else:
                    index = self.parse_expression()
                    if self.current().type == TokenType.COLON:
                        self.advance()
                        start = index
                        end = None
                        step = None
                        if self.current().type != TokenType.RBRACKET and not (
                            self.current().type == TokenType.COLON
                        ):
                            end = self.parse_expression()
                        if self.current().type == TokenType.COLON:
                            self.advance()
                            if self.current().type != TokenType.RBRACKET:
                                step = self.parse_expression()
                        self.expect(TokenType.RBRACKET, '期望 "]"')
                        expr = SliceAccess(expr, start, end, step)
                    else:
                        self.expect(TokenType.RBRACKET, '期望 "]"')
                        expr = IndexAccess(expr, index)
            else:
                break
        return expr

    def parse_primary(self):
        if self.current().type == TokenType.NUMBER:
            token = self.advance()
            return NumberLiteral(token.value)

        if self.current().type == TokenType.STRING:
            token = self.advance()
            return StringLiteral(token.value)

        if self.is_keyword('TRUE'):
            self.advance()
            return BooleanLiteral(True)

        if self.is_keyword('FALSE'):
            self.advance()
            return BooleanLiteral(False)

        if self.is_keyword('NULL'):
            self.advance()
            return NullLiteral()

        if self.is_keyword('THIS'):
            self.advance()
            return ThisExpression()

        if self.is_keyword('NEW'):
            self.advance()
            class_token = self.expect(TokenType.IDENTIFIER, '期望类名')
            self.expect(TokenType.LPAREN, '期望 "("')
            args = []
            while self.current().type != TokenType.RPAREN:
                if args:
                    self.expect(TokenType.COMMA, '期望 ","')
                args.append(self.parse_expression())
            self.expect(TokenType.RPAREN, '期望 ")"')
            return NewExpression(class_token.value, args)

        if self.is_keyword('FUNC'):
            return self.parse_lambda_expression()

        if self.current().type == TokenType.IDENTIFIER:
            token = self.advance()
            return Identifier(token.value)

        if self.current().type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN, '期望 ")"')
            return expr

        if self.current().type == TokenType.LBRACKET:
            return self.parse_list_or_comprehension()

        if self.current().type == TokenType.LBRACE:
            return self.parse_dict_literal()

        self.error(f'意外的标记: {self.current().value!r}')

    def parse_lambda_expression(self):
        self.advance()
        self.expect(TokenType.LPAREN, '期望 "("')
        params = []
        defaults = []
        has_default = False
        while self.current().type != TokenType.RPAREN:
            if params:
                self.expect(TokenType.COMMA, '期望 ","')
            param_token = self.expect(TokenType.IDENTIFIER, '期望参数名')
            params.append(param_token.value)
            if self.match(TokenType.ASSIGN):
                default_val = self.parse_expression()
                defaults.append(default_val)
                has_default = True
            else:
                if has_default:
                    self.error('有默认值的参数后不能再有无默认值的参数')
                defaults.append(None)
        self.expect(TokenType.RPAREN, '期望 ")"')
        self.skip_newlines()
        body = self.parse_block()
        return LambdaExpression(params, body)

    def parse_list_or_comprehension(self):
        self.expect(TokenType.LBRACKET, '期望 "["')
        self.skip_newlines()
        if self.current().type == TokenType.RBRACKET:
            self.advance()
            return ListLiteral([])

        first = self.parse_expression()
        self.skip_newlines()

        if self.is_keyword('FOR') and isinstance(first, (Identifier, BinaryOp, FuncCall)):
            return self._finish_list_comprehension(first)

        elements = [first]
        while self.match(TokenType.COMMA):
            self.skip_newlines()
            if self.current().type == TokenType.RBRACKET:
                break
            elements.append(self.parse_expression())
            self.skip_newlines()

        self.expect(TokenType.RBRACKET, '期望 "]"')
        return ListLiteral(elements)

    def _finish_list_comprehension(self, expr):
        if not self.is_keyword('FOR'):
            self.error('列表推导式期望 "遍历" 关键字')
        self.advance()
        var_token = self.expect(TokenType.IDENTIFIER, '期望循环变量名')
        var_name = var_token.value
        if not self.is_keyword('IN'):
            self.error('期望 "在" 关键字')
        self.advance()
        iterable = self.parse_expression()
        condition = None
        if self.is_keyword('IF'):
            self.advance()
            condition = self.parse_expression()
        self.expect(TokenType.RBRACKET, '期望 "]"')
        return ListComprehension(var_name, iterable, expr, condition)

    def parse_dict_literal(self):
        self.expect(TokenType.LBRACE, '期望 "{"')
        self.skip_newlines()
        if self.current().type == TokenType.RBRACE:
            self.advance()
            return DictLiteral([])

        pairs = []
        key = self.parse_expression()
        self.expect(TokenType.COLON, '期望 ":"')
        value = self.parse_expression()
        pairs.append((key, value))
        self.skip_newlines()

        while self.match(TokenType.COMMA):
            self.skip_newlines()
            if self.current().type == TokenType.RBRACE:
                break
            key = self.parse_expression()
            self.expect(TokenType.COLON, '期望 ":"')
            value = self.parse_expression()
            pairs.append((key, value))
            self.skip_newlines()

        self.expect(TokenType.RBRACE, '期望 "}"')
        return DictLiteral(pairs)
