#!/usr/bin/python
# -*- coding: utf-8 -*-

"""コードを構文解析して得られた抽象構文木から
    元のコードを復元するモジュール"""

from __future__ import unicode_literals, print_function
import ast


# code analysis and restoration section
def restore_code(nodelist, indent=1):
    if isinstance(nodelist, ast.NullNode):
        pass

    # top level
    elif isinstance(nodelist, ast.ExternalDeclarationList):
        for i in range(len(nodelist.nodes)):
            restore_code(nodelist.nodes[i])
        print("")

    # declaration
    elif isinstance(nodelist, ast.Declaration):
        print_type_specifier(nodelist.type_specifier)
        restore_code(nodelist.declarator_list)
        print("; ", end="")
        print("")

    elif isinstance(nodelist, ast.DeclaratorList):
        if nodelist.length() > 1:
            for i in range(nodelist.length() - 1):
                restore_code(nodelist.nodes[i])
                print(", ", end="")
            restore_code(nodelist.nodes[nodelist.length()-1])
        elif nodelist.length() == 1: # declarator-list := <declarator>
            restore_code(nodelist.nodes[0]) # declarator

    elif isinstance(nodelist, ast.Declarator):
        print_kind(nodelist.kind)
        restore_code(nodelist.direct_declarator)

    elif isinstance(nodelist, ast.DirectDeclarator):
        print_identifier(nodelist.identifier)

    elif isinstance(nodelist, ast.DirectArrayDeclarator):
        print_identifier(nodelist.identifier)
        print("[", end="")
        print_number(nodelist.constant)
        print("]", end="")

    # function
    elif isinstance(nodelist, ast.FunctionPrototype):
        print_type_specifier(nodelist.type_specifier)
        restore_code(nodelist.function_declarator)
        print(";")

    elif isinstance(nodelist, ast.FunctionDefinition):
        print_type_specifier(nodelist.type_specifier)
        restore_code(nodelist.function_declarator)
        restore_code(nodelist.compound_statement, indent=0)

    elif isinstance(nodelist, ast.FunctionDeclarator):
        print_kind(nodelist.kind)
        restore_code(nodelist.identifier)
        print("(", end="")
        restore_code(nodelist.parameter_type_list)
        print(") ", end="")

    # parameter
    elif isinstance(nodelist, ast.ParameterTypeList):
        if nodelist.length() > 1:
            for i in range(nodelist.length() - 1):
                restore_code(nodelist.nodes[i])
                print(", ", end="")
            restore_code(nodelist.nodes[nodelist.length()-1])
        else: # parameter-type-list := <parameter-declaration>
            restore_code(nodelist.nodes[0]) # parameter-declaration

    elif isinstance(nodelist, ast.ParameterDeclaration):
        print_type_specifier(nodelist.type_specifier)
        restore_code(nodelist.parameter_declarator)

    elif isinstance(nodelist, ast.ParameterDeclarator):
        print_kind(nodelist.kind)
        print_identifier(nodelist.identifier)

    # type specifier
    elif isinstance(nodelist, ast.TypeSpecifier):
        print_type_specifier(nodelist)

    # statement
    elif isinstance(nodelist, ast.ExpressionStatement):
        if isinstance(nodelist.expression, ast.NullNode):
            print("; ", end="")
        else:
            restore_code(nodelist.expression)
            print("; ", end="")

    elif isinstance(nodelist, ast.IfStatement):
        if isinstance(nodelist.else_statement, ast.NullNode):
            print("    if (", end="")
            restore_code(nodelist.expression, indent=0)
            print(") ", end="")
            restore_code(nodelist.then_statement, indent=1)
        else:
            print("    if (", end="")
            restore_code(nodelist.expression, indent=0)
            print(" ) ", end="")
            restore_code(nodelist.then_statement, indent=1)
            print("else ", end="")
            restore_code(nodelist.else_statement, indent=1)

    elif isinstance(nodelist, ast.WhileLoop):
        print("    while (", end="")
        restore_code(nodelist.expression, indent=0)
        print(") ", end="")
        restore_code(nodelist.statement, indent=1)

    elif isinstance(nodelist, ast.ForLoop):
        restore_code(nodelist.firstexp_statement)
        print("")
        restore_code(nodelist.whileloop_node, indent=1)

    elif isinstance(nodelist, ast.ReturnStatement):
        print("    ", end="")
        if isinstance(nodelist.return_statement, ast.NullNode):
            print("return ; ", end="")
        else:
            print("return ", end="")
            restore_code(nodelist.return_statement)
            print("; ", end="")

    # compound statement
    elif isinstance(nodelist, ast.CompoundStatement):
        print("{ ")
        restore_code(nodelist.declaration_list)
        restore_code(nodelist.statement_list, indent=indent)
        if indent == 1:
            print("    ", end="")
        print("} ", end="")

    elif isinstance(nodelist, ast.DeclarationList):
        for i in range(nodelist.length()):
            print("    ", end="")
            restore_code(nodelist.nodes[i])

    elif isinstance(nodelist, ast.StatementList):
        for i in range(nodelist.length()):
            restore_code(nodelist.nodes[i], indent=indent)
            print("")

    # expression
    elif isinstance(nodelist, ast.BinaryOperators):
        if indent == 1:
            print("    ", end="")
        if nodelist.op == "ASSIGN":
            restore_code(nodelist.left, indent=0)
            print(" = ", end="")
            restore_code(nodelist.right, indent=0)
        # elif nodelist.op == "PLUS_EQ":
        #     restore_code(nodelist.left, indent=0)
        #     print(" += ", end="")
        #     restore_code(nodelist.right, indent=0)
        # elif nodelist.op == "MINUS_EQ":
        #     restore_code(nodelist.left, indent=0)
        #     print(" -= ", end="")
        #     restore_code(nodelist.right, indent=0)
        elif nodelist.op == "OR":
            restore_code(nodelist.left, indent=0)
            print(" || ", end="")
            restore_code(nodelist.right, indent=0)
        elif nodelist.op == "AND":
            restore_code(nodelist.left, indent=0)
            print(" && ", end="")
            restore_code(nodelist.right, indent=0)
        elif nodelist.op == "EQUAL":
            restore_code(nodelist.left, indent=0)
            print(" == ", end="")
            restore_code(nodelist.right, indent=0)
        elif nodelist.op == "NEQ":
            restore_code(nodelist.left, indent=0)
            print(" != ", end="")
            restore_code(nodelist.right, indent=0)
        elif nodelist.op == "LT":
            restore_code(nodelist.left, indent=0)
            print(" < ", end="")
            restore_code(nodelist.right, indent=0)
        elif nodelist.op == "GT":
            restore_code(nodelist.left, indent=0)
            print(" > ", end="")
            restore_code(nodelist.right, indent=0)
        elif nodelist.op == "LEQ":
            restore_code(nodelist.left, indent=0)
            print(" <= ", end="")
            restore_code(nodelist.right, indent=0)
        elif nodelist.op == "GEQ":
            restore_code(nodelist.left, indent=0)
            print(" >= ", end="")
            restore_code(nodelist.right, indent=0)
        elif nodelist.op == "PLUS":
            restore_code(nodelist.left, indent=0)
            print(" + ", end="")
            restore_code(nodelist.right, indent=0)
        elif nodelist.op == "MINUS":
            restore_code(nodelist.left, indent=0)
            print(" - ", end="")
            restore_code(nodelist.right, indent=0)
        elif nodelist.op == "TIMES":
            restore_code(nodelist.left, indent=0)
            print(" * ", end="")
            restore_code(nodelist.right, indent=0)
        elif nodelist.op == "DIVIDE":
            restore_code(nodelist.left, indent=0)
            print(" / ", end="")
            restore_code(nodelist.right, indent=0)

    # unary operators
    # elif isinstance(nodelist, ast.Negative):
    #     print("-", end="")
    #     restore_code(nodelist.expression)

    elif isinstance(nodelist, ast.Address):
        print("&", end="")
        restore_code(nodelist.expression)

    elif isinstance(nodelist, ast.Pointer):
        print("*(", end="")
        restore_code(nodelist.expression, indent=0)
        print(")", end="")

    # elif isinstance(nodelist, ast.Increment):
    #     restore_code(nodelist.expression)
    #     print("++", end="")

    # elif isinstance(nodelist, ast.Decrement):
    #     restore_code(nodelist.expression)
    #     print("--", end="")

    elif isinstance(nodelist, ast.FunctionExpression):
        print("    ", end="")
        print_identifier(nodelist.identifier)
        print("(", end="")
        restore_code(nodelist.argument_expression)
        print(")", end="")

    elif isinstance(nodelist, ast.ArrayExpression):
        restore_code(nodelist.postfix_expr)
        print("[", end="")
        restore_code(nodelist.expression, indent=0)
        print("]", end="")

    elif isinstance(nodelist, ast.ArgumentExpressionList):
        if nodelist.length() > 1:
            for i in range(nodelist.length() - 1):
                restore_code(nodelist.nodes[i])
                print(", ", end="")
            restore_code(nodelist.nodes[nodelist.length()-1])
        else:
            restore_code(nodelist.nodes[0])

    elif isinstance(nodelist, ast.Number):
        print_number(nodelist)

    elif isinstance(nodelist, ast.Identifier):
        print_identifier(nodelist)


# print section
def print_number(class_number):
    print("{0}".format(class_number.value), end="")

def print_identifier(class_identifier):
    print("{0}".format(class_identifier.identifier), end="")

def print_type_specifier(class_type_specifier):
    print("{0} ".format(class_type_specifier.type_specifier), end="")

def print_kind(class_declarator_kind):
    if class_declarator_kind == "NORMAL":
        pass
    elif class_declarator_kind == "POINTER":
        print("*", end="")
