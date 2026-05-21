from enum import Enum, auto
from dataclasses import dataclass


class TokenType(Enum):
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()
    KEYWORD = auto()

    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    POWER = auto()

    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS = auto()
    GREATER = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()

    ASSIGN = auto()
    PLUS_ASSIGN = auto()
    MINUS_ASSIGN = auto()
    MULTIPLY_ASSIGN = auto()
    DIVIDE_ASSIGN = auto()

    AND = auto()
    OR = auto()
    NOT = auto()

    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()

    COMMA = auto()
    DOT = auto()
    COLON = auto()
    SEMICOLON = auto()
    ARROW = auto()
    QUESTION = auto()

    NEWLINE = auto()
    EOF = auto()


KEYWORDS = {
    '变量': TokenType.KEYWORD,
    '常量': TokenType.KEYWORD,
    '如果': TokenType.KEYWORD,
    '否则如果': TokenType.KEYWORD,
    '否则': TokenType.KEYWORD,
    '当': TokenType.KEYWORD,
    '遍历': TokenType.KEYWORD,
    '在': TokenType.KEYWORD,
    '函数': TokenType.KEYWORD,
    '返回': TokenType.KEYWORD,
    '真': TokenType.KEYWORD,
    '假': TokenType.KEYWORD,
    '空': TokenType.KEYWORD,
    '且': TokenType.AND,
    '或': TokenType.OR,
    '非': TokenType.NOT,
    '中断': TokenType.KEYWORD,
    '继续': TokenType.KEYWORD,
    '类': TokenType.KEYWORD,
    '继承': TokenType.KEYWORD,
    '这个': TokenType.KEYWORD,
    '新': TokenType.KEYWORD,
    '尝试': TokenType.KEYWORD,
    '捕获': TokenType.KEYWORD,
    '最终': TokenType.KEYWORD,
    '抛出': TokenType.KEYWORD,
    '导入': TokenType.KEYWORD,
    '作为': TokenType.KEYWORD,
    '从': TokenType.KEYWORD,
    '是': TokenType.KEYWORD,
    '属于': TokenType.KEYWORD,
}

KEYWORD_NAMES = {
    '变量': 'VAR',
    '常量': 'CONST',
    '如果': 'IF',
    '否则如果': 'ELIF',
    '否则': 'ELSE',
    '当': 'WHILE',
    '遍历': 'FOR',
    '在': 'IN',
    '函数': 'FUNC',
    '返回': 'RETURN',
    '真': 'TRUE',
    '假': 'FALSE',
    '空': 'NULL',
    '且': 'AND',
    '或': 'OR',
    '非': 'NOT',
    '中断': 'BREAK',
    '继续': 'CONTINUE',
    '类': 'CLASS',
    '继承': 'EXTENDS',
    '这个': 'THIS',
    '新': 'NEW',
    '尝试': 'TRY',
    '捕获': 'CATCH',
    '最终': 'FINALLY',
    '抛出': 'RAISE',
    '导入': 'IMPORT',
    '作为': 'AS',
    '从': 'FROM',
    '是': 'IS',
    '属于': 'INSTANCEOF',
}


@dataclass
class Token:
    type: TokenType
    value: any
    line: int
    column: int

    def __repr__(self):
        return f'Token({self.type.name}, {self.value!r}, 行{self.line}:{self.column})'


class LexerError(Exception):
    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f'词法错误 第{line}行 第{column}列: {message}')


class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def error(self, message):
        raise LexerError(message, self.line, self.column)

    def peek(self, offset=0):
        pos = self.pos + offset
        if pos < len(self.source):
            return self.source[pos]
        return '\0'

    def advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def match(self, expected):
        if self.pos < len(self.source) and self.source[self.pos] == expected:
            self.advance()
            return True
        return False

    def skip_whitespace(self):
        while self.pos < len(self.source) and self.source[self.pos] in ' \t\r':
            self.advance()

    def skip_comment(self):
        if self.pos + 1 < len(self.source):
            two = self.source[self.pos:self.pos + 2]
            if two == '//':
                while self.pos < len(self.source) and self.source[self.pos] != '\n':
                    self.advance()
                return True
            if two == '/*':
                self.advance()
                self.advance()
                while self.pos + 1 < len(self.source):
                    if self.source[self.pos] == '*' and self.source[self.pos + 1] == '/':
                        self.advance()
                        self.advance()
                        return True
                    self.advance()
                self.error('未闭合的多行注释')
        return False

    def read_string(self, quote):
        start_line = self.line
        start_col = self.column
        self.advance()
        result = []
        while self.pos < len(self.source):
            ch = self.source[self.pos]
            if ch == '\\':
                self.advance()
                if self.pos >= len(self.source):
                    self.error('未闭合的字符串')
                esc = self.advance()
                escape_map = {
                    'n': '\n', 't': '\t', 'r': '\r', '\\': '\\',
                    "'": "'", '"': '"', '0': '\0',
                }
                result.append(escape_map.get(esc, esc))
            elif ch == quote:
                self.advance()
                return Token(TokenType.STRING, ''.join(result), start_line, start_col)
            else:
                result.append(self.advance())
        self.error('未闭合的字符串')

    def read_number(self):
        start_line = self.line
        start_col = self.column
        result = []
        is_float = False
        while self.pos < len(self.source) and (self.source[self.pos].isdigit() or self.source[self.pos] == '.'):
            if self.source[self.pos] == '.':
                if is_float:
                    break
                if self.pos + 1 < len(self.source) and self.source[self.pos + 1].isdigit():
                    is_float = True
                else:
                    break
            result.append(self.advance())
        value = ''.join(result)
        if is_float:
            return Token(TokenType.NUMBER, float(value), start_line, start_col)
        return Token(TokenType.NUMBER, int(value), start_line, start_col)

    def read_identifier_or_keyword(self):
        start_line = self.line
        start_col = self.column
        result = []
        while self.pos < len(self.source):
            ch = self.source[self.pos]
            if self._is_identifier_char(ch):
                result.append(self.advance())
            else:
                break
        word = ''.join(result)
        sorted_keywords = sorted(KEYWORDS.keys(), key=len, reverse=True)
        for kw in sorted_keywords:
            if word == kw:
                return Token(KEYWORDS[kw], kw, start_line, start_col)
        if word in ('且',):
            return Token(TokenType.AND, word, start_line, start_col)
        if word in ('或',):
            return Token(TokenType.OR, word, start_line, start_col)
        if word in ('非',):
            return Token(TokenType.NOT, word, start_line, start_col)
        return Token(TokenType.IDENTIFIER, word, start_line, start_col)

    def _is_identifier_char(self, ch):
        if ch.isalpha() or ch == '_' or ch.isdigit():
            return True
        if '\u4e00' <= ch <= '\u9fff':
            return True
        return False

    def _is_identifier_start(self, ch):
        if ch.isalpha() or ch == '_':
            return True
        if '\u4e00' <= ch <= '\u9fff':
            return True
        return False

    def tokenize(self):
        while self.pos < len(self.source):
            self.skip_whitespace()
            if self.pos >= len(self.source):
                break

            if self.skip_comment():
                continue

            ch = self.source[self.pos]
            start_line = self.line
            start_col = self.column

            if ch == '\n':
                if self.tokens and self.tokens[-1].type != TokenType.NEWLINE:
                    self.tokens.append(Token(TokenType.NEWLINE, '\\n', start_line, start_col))
                self.advance()
                continue

            if ch in ('"', "'"):
                self.tokens.append(self.read_string(ch))
                continue

            if ch.isdigit():
                self.tokens.append(self.read_number())
                continue

            if self._is_identifier_start(ch):
                self.tokens.append(self.read_identifier_or_keyword())
                continue

            if ch == '+':
                self.advance()
                if self.match('='):
                    self.tokens.append(Token(TokenType.PLUS_ASSIGN, '+=', start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.PLUS, '+', start_line, start_col))
                continue

            if ch == '-':
                self.advance()
                if self.match('='):
                    self.tokens.append(Token(TokenType.MINUS_ASSIGN, '-=', start_line, start_col))
                elif self.match('>'):
                    self.tokens.append(Token(TokenType.ARROW, '->', start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.MINUS, '-', start_line, start_col))
                continue

            if ch == '*':
                self.advance()
                if self.match('='):
                    self.tokens.append(Token(TokenType.MULTIPLY_ASSIGN, '*=', start_line, start_col))
                elif self.match('*'):
                    self.tokens.append(Token(TokenType.POWER, '**', start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.MULTIPLY, '*', start_line, start_col))
                continue

            if ch == '/':
                self.advance()
                if self.match('='):
                    self.tokens.append(Token(TokenType.DIVIDE_ASSIGN, '/=', start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.DIVIDE, '/', start_line, start_col))
                continue

            if ch == '%':
                self.advance()
                self.tokens.append(Token(TokenType.MODULO, '%', start_line, start_col))
                continue

            if ch == '=':
                self.advance()
                if self.match('='):
                    self.tokens.append(Token(TokenType.EQUAL, '==', start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.ASSIGN, '=', start_line, start_col))
                continue

            if ch == '!':
                self.advance()
                if self.match('='):
                    self.tokens.append(Token(TokenType.NOT_EQUAL, '!=', start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.NOT, '!', start_line, start_col))
                continue

            if ch == '<':
                self.advance()
                if self.match('='):
                    self.tokens.append(Token(TokenType.LESS_EQUAL, '<=', start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.LESS, '<', start_line, start_col))
                continue

            if ch == '>':
                self.advance()
                if self.match('='):
                    self.tokens.append(Token(TokenType.GREATER_EQUAL, '>=', start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.GREATER, '>', start_line, start_col))
                continue

            if ch == '(':
                self.advance()
                self.tokens.append(Token(TokenType.LPAREN, '(', start_line, start_col))
                continue
            if ch == ')':
                self.advance()
                self.tokens.append(Token(TokenType.RPAREN, ')', start_line, start_col))
                continue
            if ch == '{':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACE, '{', start_line, start_col))
                continue
            if ch == '}':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACE, '}', start_line, start_col))
                continue
            if ch == '[':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACKET, '[', start_line, start_col))
                continue
            if ch == ']':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACKET, ']', start_line, start_col))
                continue

            if ch == ',':
                self.advance()
                self.tokens.append(Token(TokenType.COMMA, ',', start_line, start_col))
                continue
            if ch == '.':
                self.advance()
                self.tokens.append(Token(TokenType.DOT, '.', start_line, start_col))
                continue
            if ch == ':':
                self.advance()
                self.tokens.append(Token(TokenType.COLON, ':', start_line, start_col))
                continue
            if ch == ';':
                self.advance()
                self.tokens.append(Token(TokenType.SEMICOLON, ';', start_line, start_col))
                continue
            if ch == '?':
                self.advance()
                self.tokens.append(Token(TokenType.QUESTION, '?', start_line, start_col))
                continue

            self.error(f'未知字符: {ch!r}')

        if self.tokens and self.tokens[-1].type != TokenType.NEWLINE:
            self.tokens.append(Token(TokenType.NEWLINE, '\\n', self.line, self.column))
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens
