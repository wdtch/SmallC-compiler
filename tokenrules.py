#!/usr/bin/python
# -*- coding: utf-8 -*-

'''lexとyaccで用いるトークンをまとめたモジュール'''

#  reserved words list
reserved = {
    'return': 'RETURN',
    'if':     'IF',
    'else':   'ELSE',
    'while':  'WHILE',
    'for':    'FOR',
    'int':    'INT',
    'void':   'VOID',
}

# token list
tokens = (
    # operators
    'NUMBER',   # int-type number
    'PLUS',     # '+'
    'MINUS',    # '-'
    'TIMES',    # '*'
    'DIVIDE',   # '/'
    'AND',      # '&&'
    'OR',       # '||'
    'LT',       # '<'
    'LEQ',      # '<='
    'GT',       # '>'
    'GEQ',      # '>='
    'EQUAL',    # '=='
    'NEQ',      # '!='
    'INC',      # '++'
    'DEC',      # '--'

    # assignments
    'ASSIGN',     # '='
    'PLUS_EQ',    # '+='
    'MINUS_EQ',   # '-='

    # literals
    'ID',       # identifier

    # symbols
    'LPAREN',     # '('
    'RPAREN',     # ')'
    'LBRACE',     # '{'
    'RBRACE',     # '}'
    'LBRACKET',   # '['
    'RBRACKET',   # ']'
    'COMMA',      # ','
    'SEMICOLON',  # ';'

    # pointer
    'ADDRESS'      # '&'

) + tuple(reserved.values())