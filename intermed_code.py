#!/usr/bin/python
# -*- coding: utf-8 -*-

import ast
import semantic_analyzer as sa
import collections

# リストを平らにする関数の定義
def flatten(l):
    i = 0
    while i < len(l):
        while isinstance(l[i], collections.Iterable):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return l


# 中間命令を表現するクラス群

# 変数宣言
class VarDecl(object):

    def __init__(self, var):
        self.var = var

    def __eq__(self, other):
        # return self.var == other.var
        return self.__dict__ == other.__dict__


# 関数宣言
class FunctionDefinition(object):

    def __init__(self, var, params, body):
        self.var = var
        self.params = params
        self.body = body

    def __eq__(self, other):
        # return self.var == other.var and self.params == other.params and self.body == other.body
        return self.__dict__ == other.__dict__


# 文
class EmptyStatement(object):

    def __init__(self):
        pass

    def __eq__(self, other):
        if isinstance(other, EmptyStatement):
            return True
        else:
            return False


class LetStatement(object):

    def __init__(self, var, exp):
        self.var = var
        self.exp = exp

    def __eq__(self, other):
        # return self.var == other.var and self.exp == other.exp
        return self.__dict__ == other.__dict__

class WriteStatement(object):

    def __init__(self, dest, src):
        self.dest = dest
        self.src = src

    def __eq__(self, other):
        # return self.dest == other.dest and self.src == other.src
        return self.__dict__ == other.__dict__


class ReadStatement(object):

    def __init__(self, dest, src):
        self.dest = dest
        self.src = src

    def __eq__(self, other):
        # return self.dest == other.dest and self.src == other.src
        return self.__dict__ == other.__dict__


class IfStatement(object):

    def __init__(self, var, then_stmt, else_stmt):
        self.var = var
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

    def __eq__(self, other):
        # return self.var == other.var and self.then_stmt == other.then_stmt and self.else_stmt == other.else_stmt
        return self.__dict__ == other.__dict__


class WhileStatement(object):

    def __init__(self, var, stmt):
        self.var = var
        self.stmt = stmt

    def __eq__(self, other):
        # return self.var == other.var and self.stmt == other.stmt
        return self.__dict__ == other.__dict__


class CallStatement(object):

    def __init__(self, dest, function, variables):
        self.dest = dest
        self.function = function
        self.variables = variables

    def __eq__(self, other):
        # return self.dest == other.dest and self.function == other.function and self.variables == other.variables
        return self.__dict__ == other.__dict__


class ReturnStatement(object):

    def __init__(self, var):
        self.var = var

    def __eq__(self, other):
        # return self.var == other.var
        return self.__dict__ == other.__dict__


class PrintStatement(object):

    def __init__(self, var):
        self.var = var

    def __eq__(self, other):
        # return self.var == other.var
        return self.__dict__ == other.__dict__


class CompoundStatement(object):

    def __init__(self, decls, stmts):
        self.decls = decls
        self.stmts = stmts

    def __eq__(self, other):
        # return self.decls == other.decls and self.stmts == other.stmts
        return self.__dict__ == other.__dict__


# 式
class VarExpression(object):

    def __init__(self, var):
        self.var = var

    def __eq__(self, other):
        # return self.var == other.var
        return self.__dict__ == other.__dict__


class IntExpression(object):

    def __init__(self, num):
        self.num = num

    def __eq__(self, other):
        # return self.num == other.num
        return self.__dict__ == other.__dict__


class ArithmeticOperation(object):

    def __init__(self, op, var_left, var_right):
        self.var_left = var_left
        self.var_right = var_right

    def __eq__(self, other):
        # return self.var_left == other.var_left and self.var_right == other.var_right
        return self.__dict__ == other.__dict__


class RelationalExpression(object):

    def __init__(self, op, var_left, var_right):
        self.var_left = var_left
        self.var_right = var_right

    def __eq__(self, other):
        # return self.var_left == other.var_left and self.var_right == other.var_right
        return self.__dict__ == other.__dict__


class AddressExpression(object):

    def __init__(self, var):
        self.var = var

    def __eq__(self, other):
        # return self.var == other.var
        return self.__dict__ == other.__dict__


# 中間命令列を生成するためのクラス群
class IntermedCodeGenerator(object):

    """中間命令列を生成するために必要なインスタンスとメソッドをまとめたクラス
       中間命令列を格納するリストと、変換関数からなる"""

    def __init__(self, nodelist):
        self.ast_node = nodelist
        self.intermed_code_list = []
        self.tvg = TempVariableGenerator()

    def intermed_code_generator(self):
        """抽象構文木を引数として受け取り(or インスタンス変数のast_nodeを更新し)、
           再帰的に抽象構文木のノードを辿りながら、ノードの種類に応じて中間表現を
           生成しリストに加える
           返り値として生成された中間表現列のリストを返す"""
        if isinstance(ast_node, ast.ExternalDeclarationList):
            for node in ast_node.nodes:
                ast_node = node
                self.intermed_code_generator()

        elif isinstance(ast_node, ast.Declaration):
            intermed_decl_list = self.intermed_code_vardecl(ast_node)
            self.intermed_code_list.append(intermed_decl_list)

        elif isinstance(ast_node, ast.FunctionPrototype):
            pass

        elif isinstance(ast_node, ast.FunctionDefinition):
            intermed_code_fundef(ast_node)
        return self.intermed_code_list

    def intermed_code_vardecl(self, decl):
        """Declarationを表す抽象構文木のノードを中間命令列に変換する
           引数として変換する宣言のノードをとる
           返り値として変換結果の中間命令列のリストを返す"""
        itmd_decllist = []
        for declarator in decl.declarator_list.nodes:
            decl_struct = declarator.direct_declarator.identifier.identifier
            itmd_decllist.append(VarDecl(decl_struct))
        return itmd_decllist

    def intermed_code_exp(self, x, exp):
        """Expressionを表す抽象構文木のノードを、
           expを評価してxに結果を代入する中間命令列に変換する
           引数として代入先の変数(生成された一時変数)と、変換するノードをとる
           返り値として変換結果の中間命令列のリストを返す"""
        itmd_explist = []

        if isinstance(exp, ast.Number):
            intermed_num = IntExpression(exp.value)
            let_num = LetStatement(x, intermed_num)
            itmd_explist.append(let_num)

        elif isinstance(exp, ast.Identifier):
            intermed_var = VarExpression(exp.identifier)
            let_var = LetStatement(x, intermed_var)
            itmd_explist.append(let_var)

        elif isinstance(exp, ast.BinaryOperators):
            temp0 = self.tvg.newvardecl()
            temp1 = self.tvg.newvardecl()

            if exp.op == "PLUS" or \
               exp.op == "MINUS" or \
               exp.op == "TIMES" or \
               exp.op == "DIVIDE":
                itmd_left = self.intermed_code_exp(temp0, exp.left)
                itmd_right = self.intermed_code_exp(temp1, exp.right)
                itmd_aop = ArithmeticOperation(exp.op, temp0, temp1)
                itmd_aop_let = LetStatement(x, itmd_aop)
                aop_list = [itmd_left, itmd_right, itmd_aop_let]
                itmd_explist = aop_list

            elif exp.op == "EQUAL" or \
                 exp.op == "NEQ" or \
                 exp.op == "LT" or \
                 exp.op == "GT" or \
                 exp.op == "LEQ" or \
                 exp.op == "GEQ":

                itmd_left = self.intermed_code_exp(temp0, exp.left)
                itmd_right = self.intermed_code_exp(temp1, exp.right)
                itmd_relop = RelationalExpression(exp.op, temp0, temp1)
                itmd_relop_let = LetStatement(x, itmd_relop)
                relop_list = [itmd_left, itmd_right, itmd_relop_let]
                itmd_explist = relop_list

        elif isinstance(exp, ast.Address):
            intermed_varp = AddressExpression(exp.expression.identifier)
            let_yp = LetStatement(x, intermed_varp)
            itmd_explist.append(let_yp)

        return flatten(itmd_explist)

    def intermed_code_statement(self, statement):
        """Statementを表す抽象構文木のノードを中間命令列に変換する
           引数として変換する文のノードをとる
           返り値として変換結果の中間命令列のリストを返す"""
        itmd_stmtlist = []
        return itmd_stmtlist

    def intermed_code_fundef(self, fundef):
        """FunctionDefinitionを表す抽象構文木のノードを中間命令列に変換する
           引数として変換する関数定義のノードをとる
           返り値として変換結果の中間命令列のリストを返す"""
        itmd_fundeflist = []
        # declaratorに対する処理
        # self.ast_node = fundef.compound_statement
        # self.intermed_code_generator()
        return itmd_fundeflist


class TempVariableGenerator(object):

    """中間表現を生成する際に必要な一時変数を生成するクラス
       インスタンスとしてカウンタを持ち、メソッドとして新しい
       一時変数の名前を返すnewvardeclと、カウンタの値を0にリセットする
       resetを持つ"""

    def __init__(self):
        self.counter = 0

    def newvardecl(self):
        tempvar_name = "_t" + str(self.counter)
        tempvar_decl = sa.Decl(tempvar_name, 0, "temp", "int")
        self.counter += 1
        return tempvar_decl

    def reset(self):
        self.counter = 0
