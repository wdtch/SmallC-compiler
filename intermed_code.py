#!/usr/bin/python
# -*- coding: utf-8 -*-

import ast
import semantic_analyzer as sa
import unittest


# 中間命令を表現するクラス群

# 変数宣言
class VarDecl(object):

    def __init__(self, var):
        self.var = var


# 関数宣言
class FunctionDefinition(object):

    def __init__(self, var, params, body):
        self.var = var
        self.params = params
        self.body = body


# 文
class EmptyStatement(object):

    def __init__(self):
        pass


class LetStatement(object):

    def __init__(self, var, exp):
        self.var = var
        self.exp = exp


class WriteStatement(object):

    def __init__(self, dest, src):
        self.dest = dest
        self.src = src


class ReadStatement(object):

    def __init__(self, dest, src):
        self.dest = dest
        self.src = src


class IfStatement(object):

    def __init__(self, var, then_stmt, else_stmt):
        self.var = var
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt


class WhileStatement(object):

    def __init__(self, var, stmt):
        self.var = var
        self.stmt = stmt


class CallStatement(object):

    def __init__(self, dest, function, variables):
        self.dest = dest
        self.function = function
        self.variables = variables


class ReturnStatement(object):

    def __init__(self, var):
        self.var = var


class PrintStatement(object):

    def __init__(self, var):
        self.var = var


class CompoundStatement(object):

    def __init__(self, decls, stmts):
        self.decls = decls
        self.stmts = stmts


# 式
class VarExpression(object):

    def __init__(self, var):
        self.var = var


class IntExpression(object):

    def __init__(self, num):
        self.num = num


class ArithmeticOperation(object):

    def __init__(self, op, var_left, var_right):
        self.var_left = var_left
        self.var_right = var_right


class RelationalExpression(object):

    def __init__(self, op, var_left, var_right):
        self.var_left = var_left
        self.var_right = var_right


class AddressExpression(object):

    def __init__(self, var):
        self.var = var


# 中間命令列を生成するためのクラス群
class IntermedCodeGenerator(object):

    """中間命令列を生成するために必要なインスタンスとメソッドをまとめたクラス
       中間命令列を格納するリストと、変換関数からなる"""

    def __init__(self, nodelist):
        self.ast_top = nodelist
        self.intermed_code_list = []
        self.tempvargen = TempVariableGenerator()

    def intermed_code_generator(self, nodelist):
        """抽象構文木を引数として受け取り、再帰的に抽象構文木のノードを
           辿りながら、ノードの種類に応じて中間表現を生成しリストに加える"""
        if isinstance(nodelist, ast.ExternalDeclarationList):
            for node in nodelist.nodes:
                self.intermed_code_generator(node)

    def intermed_code_vardecl(self, decl):
        """Declarationを表す抽象構文木のノードを中間命令列に変換する
           引数として変換する宣言のノードをとる"""
            pass

    def intermed_code_exp(self, x, exp):
        """Expressionを表す抽象構文木のノードを、
           expを評価してxに結果を代入する中間命令列に変換する
           引数として代入先の変数(生成された一時変数)と、変換するノードをとる"""
        pass

    def intermed_code_statement(self, statement):
        """Statementを表す抽象構文木のノードを中間命令列に変換する
           引数として変換する文のノードをとる"""
        pass

    def intermed_code_fundef(self, fundef):
        """FunctionDefinitionを表す抽象構文木のノードを中間命令列に変換する
           引数として変換する関数定義のノードをとる"""
        pass


class TempVariableGenerator(object):

    """中間表現を生成する際に必要な一時変数を生成するクラス
       インスタンスとしてカウンタを持ち、メソッドとして新しい
       一時変数の名前を返すnewvarと、カウンタの値を0にリセットする
       resetを持つ"""

    def __init__(self):
        self.counter = 0

    def newvar(self):
        tempvar_name = "_t" + str(self.counter)
        self.counter += 1
        return tempvar_name

    def reset(self):
        self.counter = 0
