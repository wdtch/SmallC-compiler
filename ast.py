#!/usr/bin/python
# -*- coding: utf-8 -*-

"""抽象構文木を構築するためのモジュール"""

import ply.lex as lex
import ply.yacc as yacc

# parent Node


class Node(object):
    pass


class NullNode(Node):
    pass


# Nodes

# Number
class Number(Node):

    def __init__(self, value):
        self.value = value

# Declaration


class Declaration(Node):

    def __init__(self, type_specifier, declator_list):
        self.type_specifier = type_specifier
        self.declarator_list = declator_list


class Declarator(Node):

    def __init__(self, kind, direct_declarator):
        self.kind = kind
        self.direct_declarator = direct_declarator


class DirectDeclarator(Node):

    def __init__(self, identifier):
        self.identifier = identifier


class DirectArrayDeclarator(Node):

    def __init__(self, identifier, constant):
        self.identifier = identifier
        self.constant = constant

# Identifier


class Identifier(Node):

    def __init__(self, identifier, lineno):
        self.identifier = identifier
        self.lineno = lineno

# Parameter


class ParameterDeclaration(Node):

    def __init__(self, typespcf, paramdec):
        self.type_specifier = typespcf
        self.parameter_declarator = paramdec


class ParameterDeclarator(Node):

    def __init__(self, kind, identifier):
        self.kind = kind
        self.identifier = identifier

# Type Specifier


class TypeSpecifier(Node):

    def __init__(self, typespcf):
        self.type_specifier = typespcf

# Binary Operators


class BinaryOperators(Node):

    def __init__(self, op, left, right, lineno):
        self.op = op
        self.left = left
        self.right = right
        self.lineno = lineno

# Unary Operators


class UnaryOperator(Node):

    def __init__(self, node, lineno):
        self.expression = node
        self.lineno = lineno

# class Negative(UnaryOperator):
    # pass


class Address(UnaryOperator):
    pass


class Pointer(UnaryOperator):
    pass


class ExpressionStatement(Node):

    def __init__(self, expr):
        self.expression = expr


# conditional statements

class IfStatement(Node):

    def __init__(self, expr, then_stmt, else_stmt, lineno):
        self.expression = expr
        self.then_statement = then_stmt
        self.else_statement = else_stmt
        self.lineno = lineno


class WhileLoop(Node):

    def __init__(self, expr, stmt, lineno):
        self.expression = expr
        self.statement = stmt
        self.lineno = lineno


class ForLoop(Node):

    def __init__(self, stmt_firstexp, whilenode):
        self.firstexp_statement = stmt_firstexp
        self.whileloop_node = whilenode


class ReturnStatement(Node):

    def __init__(self, returnstmt):
        self.return_statement = returnstmt


class CompoundStatement(Node):

    def __init__(self, dec_list, stmt_list):
        self.declaration_list = dec_list
        self.statement_list = stmt_list


class FunctionDefinition(Node):

    def __init__(self, typespcf, funcdec, compstmt):
        self.type_specifier = typespcf
        self.function_declarator = funcdec
        self.compound_statement = compstmt


class FunctionDeclarator(Node):

    def __init__(self, kind, identifier, param_type_list):
        self.kind = kind
        self.identifier = identifier
        self.parameter_type_list = param_type_list


class FunctionPrototype(Node):

    def __init__(self, type_specifier, function_declarator):
        self.type_specifier = type_specifier
        self.function_declarator = function_declarator


class FunctionExpression(Node):

    def __init__(self, identifier, argexp, lineno=0):
        self.identifier = identifier
        self.argument_expression = argexp
        if lineno > 0:
            self.lineno = lineno


class ArrayExpression(Node):

    def __init__(self, postfix_expr, exp):
        self.postfix_expr = postfix_expr
        self.expression = exp

# NodeLists


class NodeList(Node):

    def __init__(self, node=None):
        if node is None:
            self.nodes = []
        else:
            self.nodes = [node]

    def append(self, node):
        self.nodes.append(node)

    def insert(self, index, node):
        self.nodes.insert(index, node)

    def length(self):
        return len(self.nodes)

    def printnodes(self):
        print(self.nodes)


class ExternalDeclarationList(NodeList):
    pass


class DeclarationList(NodeList):
    pass


class DeclaratorList(NodeList):
    pass


class StatementList(NodeList):
    pass


class ParameterTypeList(NodeList):
    pass


class ArgumentExpressionList(NodeList):
    pass