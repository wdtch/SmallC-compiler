#!/usr/bin/python
# -*- coding: utf-8 -*-

"""字句解析のためのモジュール"""

from __future__ import unicode_literals
import ply.lex as lex
import tokenrules

class Lexer(object):
    tokens = tokenrules.tokens

    # 正規表現によるルール
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_AND = r'&&'
    t_OR = r'\|\|'
    t_LT = r'<'
    t_LEQ = r'<='
    t_GT = r'>'
    t_GEQ = r'>='
    t_EQUAL = r'=='
    t_NEQ = r'!='
    t_INC = r'\+\+'
    t_DEC = r'--'

    t_ASSIGN = r'='
    t_PLUS_EQ = r'\+='
    t_MINUS_EQ = r'-='

    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_COMMA = r','
    t_SEMICOLON = r';'

    t_ADDRESS = r'&'

    # 正規表現とアクションコード
    def t_NUMBER(self, t):
        r'\d+'
        try:
            t.value = int(t.value)
        except ValueError:
            print("Integer value too large %d", t.value)
            t.value = 0
        return t

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = tokenrules.reserved.get(t.value,'ID')  # Check for reserved words
        return t

    def t_COMMENT(self, t):
        r'/\*[\w\W]*?\*/'
        t.lexer.lineno += t.value.count('\n')

    # スペース、タブ、改行を無視
    t_ignore = " \t\n"

    # 行番号をたどる
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    # エラー処理
    def t_error(self, t):
        print("Illegal Character: {0}".format(t.value[0]))

    def build(self, **kwargs):
        # Lexer構築
        self.lexer = lex.lex(module=self, **kwargs)

        # ここからテスト
        if __name__ == '__main__':
            while True:
                try:
                    print "Write test code."
                    data = raw_input()
                    if data == "end":
                        break
                    self.lexer.input(data)
                    while True:
                        tok = self.lexer.token()
                        if not tok:
                            # これ以上トークンはない
                            break
                        print tok
                except EOFError:
                    break

mylexer = Lexer()
mylexer.build()