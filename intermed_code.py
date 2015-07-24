#!/usr/bin/python
# -*- coding: utf-8 -*-

import ast
import semantic_analyzer as sa
# import assign_address
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
        self.localvarsize = 0
        self.paramsize = 0

    def __eq__(self, other):
        # return self.var == other.var and self.params == other.params and
        # self.body == other.body
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
        # return self.var == other.var and self.then_stmt == other.then_stmt
        # and self.else_stmt == other.else_stmt
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
        # return self.dest == other.dest and self.function == other.function
        # and self.variables == other.variables
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
        self.op = op
        self.var_left = var_left
        self.var_right = var_right

    def __eq__(self, other):
        # return self.var_left == other.var_left and self.var_right ==
        # other.var_right
        return self.__dict__ == other.__dict__


class RelationalExpression(object):

    def __init__(self, op, var_left, var_right):
        self.op = op
        self.var_left = var_left
        self.var_right = var_right

    def __eq__(self, other):
        # return self.var_left == other.var_left and self.var_right ==
        # other.var_right
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
        self.tempdecl_list = []
        self.tvg = TempVariableGenerator()
        # self.addr = assign_address.AssignAddress()


    def intermed_code_generator(self):
        """抽象構文木を引数として受け取り(or インスタンス変数のast_nodeを更新し)、
           再帰的に抽象構文木のノードを辿りながら、ノードの種類に応じて中間表現を
           生成しリストに加える
           返り値として生成された中間表現列のリストを返す"""
        if isinstance(self.ast_node, ast.ExternalDeclarationList):
            for node in self.ast_node.nodes:
                self.ast_node = node
                self.intermed_code_generator()

        elif isinstance(self.ast_node, ast.Declaration):
            intermed_global_decl = self.intermed_code_vardecl(self.ast_node)
            self.intermed_code_list.append(intermed_global_decl)

        elif isinstance(self.ast_node, ast.FunctionDefinition):
            self.intermed_code_list.append(
                self.intermed_code_fundef(self.ast_node))
            self.tempdecl_list = [] # initialize

        return flatten(self.intermed_code_list)

    def intermed_code_vardecl(self, decl):
        """Declarationを表す抽象構文木のノードを中間命令列に変換する
           引数として変換する宣言のノードをとる
           返り値として変換結果の中間命令列のリストを返す"""
        itmd_decllist = []
        if isinstance(decl, ast.NullNode):
            pass  # 空リストのまま放っておく
        else:
            if isinstance(decl, ast.DeclarationList):
                for declaration in decl.nodes:
                    for declarator in declaration.declarator_list.nodes:
                        decl_struct = declarator.direct_declarator.identifier.identifier
                        itmd_decllist.append(VarDecl(decl_struct))
            else:
                for declarator in decl.declarator_list.nodes:
                    decl_struct = declarator.direct_declarator.identifier.identifier
                    itmd_decllist.append(VarDecl(decl_struct))

        return flatten(itmd_decllist)

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

        elif isinstance(exp, ast.Pointer):
            p1 = self.tvg.newvardecl()
            self.tempdecl_list.append(VarDecl(p1))
            intermed_var = self.intermed_code_exp(p1, exp.expression)
            let_var = LetStatement(x, p1)
            itmd_explist.append(intermed_var)
            itmd_explist.append(let_var)

        elif isinstance(exp, ast.BinaryOperators):
            p1 = self.tvg.newvardecl()
            p2 = self.tvg.newvardecl()
            self.tempdecl_list.append(VarDecl(p1))
            self.tempdecl_list.append(VarDecl(p2))

            if exp.op == "PLUS" or \
               exp.op == "MINUS" or \
               exp.op == "TIMES" or \
               exp.op == "DIVIDE":

                print("Dealing with Arithmetic Operation...")
                print("op: {0}".format(exp.op))
                print("left: {0}, {1}".format(exp.left, exp.left.__dict__))
                print("right: {0}, {1}".format(exp.right, exp.right.__dict__))
                itmd_left = self.intermed_code_exp(p1, exp.left)
                itmd_right = self.intermed_code_exp(p2, exp.right)
                itmd_aop = ArithmeticOperation(exp.op, p1, p2)
                itmd_aop_let = LetStatement(x, itmd_aop)
                itmd_explist.append(itmd_left)
                itmd_explist.append(itmd_right)
                itmd_explist.append(itmd_aop_let)

            elif exp.op == "EQUAL" or \
                    exp.op == "NEQ" or \
                    exp.op == "LT" or \
                    exp.op == "GT" or \
                    exp.op == "LEQ" or \
                    exp.op == "GEQ" or \
                    exp.op == "AND" or \
                    exp.op == "OR":

                itmd_left = self.intermed_code_exp(p1, exp.left)
                itmd_right = self.intermed_code_exp(p2, exp.right)
                itmd_relop = RelationalExpression(exp.op, p1, p2)
                itmd_relop_let = LetStatement(x, itmd_relop)
                itmd_explist.append(itmd_left)
                itmd_explist.append(itmd_right)
                itmd_explist.append(itmd_relop_let)

            else:
                print("nanka akan with BinaryOperators : op = {0}".format(exp.op))

        elif isinstance(exp, ast.Address):
            p1 = self.tvg.newvardecl()
            self.tempdecl_list.append(VarDecl(p1))
            intermed_varp = self.intermed_code_exp(p1, exp.expression)
            addr_xp = AddressExpression(p1)
            itmd_explist.append(intermed_varp)
            itmd_explist.append(addr_xp)

        elif isinstance(exp, ast.FunctionExpression):
            # print関数の呼び出し
            print("function expression -> intermed code")
            print(exp.identifier.identifier)
            if isinstance(exp.identifier.identifier, sa.Decl):
                print(exp.identifier.identifier.__dict__)
            if exp.identifier.identifier.name == "print":
                p1 = self.tvg.newvardecl()
                self.tempdecl_list.append(VarDecl(p1))
                let_arg = self.intermed_code_exp(p1, exp.argument_expression.nodes[0])  # 引数は1つと仮定してもいい？
                intermed_print = PrintStatement(p1)
                itmd_explist.append(let_arg)
                itmd_explist.append(intermed_print)

            # それ以外の関数呼び出し
            else:
                tempvars = [self.tvg.newvardecl()
                            for _ in exp.argument_expression.nodes]
                for tempvar in tempvars:
                    self.tempdecl_list.append(VarDecl(tempvar))
                let_args = [self.intermed_code_exp(tempvars[i], arg) for i, arg in enumerate(
                    exp.argument_expression.nodes)]
                intermed_funccall = CallStatement(
                    x, exp.identifier.identifier, tempvars)
                for let_arg in reversed(let_args):
                    itmd_explist.append(let_arg)
                itmd_explist.append(intermed_funccall)

        return flatten(itmd_explist)

    def intermed_code_statement(self, statement):
        """Statementを表す抽象構文木のノードを中間命令列に変換する
           引数として変換する文のノードをとる
           返り値として変換結果の中間命令列のリストを返す"""
        itmd_stmtlist = []
        if isinstance(statement, ast.NullNode):
            itmd_stmtlist.append(EmptyStatement())

        elif isinstance(statement, ast.IfStatement):
            print("converting if statement ast to intermed code...")
            print("then: {0}".format(statement.then_statement))
            print("else: {0}".format(statement.else_statement))
            p1 = self.tvg.newvardecl()
            self.tempdecl_list.append(VarDecl(p1))
            let_exp = self.intermed_code_exp(p1, statement.expression)
            then_stmt = self.intermed_code_statement(statement.then_statement)
            else_stmt = self.intermed_code_statement(statement.else_statement)
            print(then_stmt)
            print(else_stmt)
            intermed_if = IfStatement(
                p1, then_stmt, else_stmt)  # リストになってるので[0]をつける…！？
            itmd_stmtlist.append(let_exp)
            itmd_stmtlist.append(intermed_if)

        elif isinstance(statement, ast.WhileLoop):
            p1 = self.tvg.newvardecl()
            self.tempdecl_list.append(VarDecl(p1))
            let_exp = self.intermed_code_exp(p1, statement.expression)
            stmt = self.intermed_code_statement(statement.statement)
            whilestmt = flatten([stmt, let_exp])
            intermed_while = WhileStatement(p1, whilestmt)
            itmd_stmtlist.append(let_exp)
            itmd_stmtlist.append(intermed_while)

        elif isinstance(statement, ast.ExpressionStatement):
            if isinstance(statement.expression, ast.BinaryOperators) and \
                statement.expression.op == "ASSIGN":
                print("intermed_code: ASSIGN statement.")

                # *x = y
                if isinstance(statement.expression.left, ast.Pointer):
                    p1 = self.tvg.newvardecl()
                    self.tempdecl_list.append(VarDecl(p1))

                    let_left = self.intermed_code_exp(
                        p1, statement.expression.left.expression)
                    itmd_stmtlist.append(let_left)

                    # 定数代入の場合右辺をintermed_code_expで評価する必要がない
                    if isinstance(statement.expression.right, ast.Number):
                        intexp = IntExpression(statement.expression.right.value)
                        itmd_stmtlist.append(WriteStatement(p1, intexp))
                    else:
                        p2 = self.tvg.newvardecl()
                        self.tempdecl_list.append(VarDecl(p2))

                        let_right = self.intermed_code_exp(p2, statement.expression.right)
                        itmd_stmtlist.append(let_right)
                        itmd_stmtlist.append(WriteStatement(p1, p2))

                # x = *y
                elif isinstance(statement.expression.right, ast.Pointer):
                    p1 = self.tvg.newvardecl()
                    p2 = self.tvg.newvardecl()
                    self.tempdecl_list.append(VarDecl(p1))
                    self.tempdecl_list.append(VarDecl(p2))

                    let_left = self.intermed_code_exp(p1, statement.expression.left)
                    let_right = self.intermed_code_exp(
                        p2, statement.expression.right.expression)
                    itmd_stmtlist.append(let_left)
                    itmd_stmtlist.append(let_right)
                    itmd_stmtlist.append(ReadStatement(p1, p2))

                # x(ただの変数) = y
                elif isinstance(statement.expression.left, ast.Identifier):
                    print("left is tadano hensuu")
                    print("op: {0}".format(statement.expression.op))
                    print("left: {0}".format(statement.expression.left.identifier.__dict__))
                    print("right: {0}".format(statement.expression.right.__dict__))
                    p1 = self.tvg.newvardecl()
                    self.tempdecl_list.append(VarDecl(p1))

                    # 右辺が定数のとき、else節の方法で右辺を処理すると無駄なストア・ロードが生じる
                    if isinstance(statement.expression.right, ast.Number):
                        intexp = IntExpression(statement.expression.right.value)
                        # let_stmt = self.intermed_code_exp(statement.expression.left, intexp)
                        let_stmt = LetStatement(statement.expression.left.identifier, intexp)
                        print("Let statement to add: {0}".format(let_stmt))
                        itmd_stmtlist.append(let_stmt)
                    else:
                        let_right = self.intermed_code_exp(p1, statement.expression.right)
                        let_stmt = LetStatement(statement.expression.left.identifier, VarExpression(p1))
                        # let_stmt = self.intermed_code_exp(statement.expression.left, p1)
                        itmd_stmtlist.append(let_right)
                        print("Let statement to add: {0}".format(let_stmt))
                        itmd_stmtlist.append(let_stmt)
                        # itmd_stmtlist.append(let_stmt)
                    # print("Let statement to add: {0}".format(let_stmt))
                    # itmd_stmtlist.append(let_stmt)

                # 存在するのか？
                else:
                    p1 = self.tvg.newvardecl()
                    p2 = self.tvg.newvardecl()
                    self.tempdecl_list.append(VarDecl(p1))
                    self.tempdecl_list.append(VarDecl(p2))
                    let_left = self.intermed_code_exp(p1, statement.expression.left)
                    let_right = self.intermed_code_exp(p2, statement.expression.right)
                    let_stmt = LetStatement(p1, p2)
                    itmd_stmtlist.append(let_left)
                    itmd_stmtlist.append(let_right)
                    itmd_stmtlist.append(let_stmt)

            else:
                p1 = self.tvg.newvardecl()
                self.tempdecl_list.append(VarDecl(p1))
                intermed_exp = self.intermed_code_exp(p1, statement.expression)
                itmd_stmtlist.append(
                    intermed_exp)

        elif isinstance(statement, ast.ReturnStatement):
            if isinstance(statement.return_statement, ast.NullNode):
                # return_stmt = EmptyStatement()
                pass
            else:
                p1 = self.tvg.newvardecl()
                self.tempdecl_list.append(VarDecl(p1))
                let_return = self.intermed_code_exp(
                    p1, statement.return_statement)
                intermed_return = ReturnStatement(p1)
                itmd_stmtlist.append(let_return)
                itmd_stmtlist.append(intermed_return)

        elif isinstance(statement, ast.CompoundStatement):
            intermed_compstmt = self.intermed_code_compstmt(statement)
            itmd_stmtlist.append(intermed_compstmt)

        return flatten(itmd_stmtlist)

    def intermed_code_compstmt(self, compstmt):
        """CompoundStatementを表す抽象構文木のノードを中間命令列に変換する
           引数として変換対象の複文のノードを取り、返り値として生成された一時変数の
           宣言を加えた中間命令を返す"""
        decl_list = []
        stmt_list = []
        for decl in compstmt.declaration_list.nodes:
            decls = self.intermed_code_vardecl(decl)
            for intermed_decl in decls:
                decl_list.append(intermed_decl)

        for statement in compstmt.statement_list.nodes:
            stmt_list.append(self.intermed_code_statement(statement))

        # for stmtelem in flatten(stmt_list):
        #     if isinstance(stmtelem, LetStatement):
        #         if isinstance(stmtelem.var, sa.Decl) \
        #                 and stmtelem.var.kind == "temp":
        #             decl_list.append(
        #                 VarDecl(stmtelem.var))

            # elif isinstance(stmtelem, CompoundStatement):
            #     self.intermed_code_compstmt(stmtelem)

        itmd_compstmt = CompoundStatement(
            flatten(decl_list), flatten(stmt_list))

        return itmd_compstmt

    def intermed_code_fundef(self, fundef):
        """FunctionDefinitionを表す抽象構文木のノードを中間命令列に変換する
           引数として変換する関数定義のノードをとる
           返り値として変換結果の中間命令列のリストを返す"""
        itmd_paramlist = []
        funcvar = fundef.function_declarator.identifier.identifier
        compstmt = fundef.compound_statement

        if not isinstance(fundef.function_declarator.parameter_type_list, ast.NullNode):
            for param in fundef.function_declarator.parameter_type_list.nodes:
                itmd_paramlist.append(
                    VarDecl(param.parameter_declarator.identifier.identifier))

        decl_list = []
        stmt_list = []
        for decl in compstmt.declaration_list.nodes:
            decls = self.intermed_code_vardecl(decl)
            for intermed_decl in decls:
                decl_list.append(intermed_decl)

        for statement in compstmt.statement_list.nodes:
            stmt_list.append(self.intermed_code_statement(statement))

        # TODO: decl_listとtempdecl_listを合わせてdecl_listとする
        decl_list.extend(self.tempdecl_list)

        itmd_compstmt = CompoundStatement(flatten(decl_list), flatten(stmt_list))
        itmd_fundef = FunctionDefinition(
            funcvar, itmd_paramlist, itmd_compstmt)

        return itmd_fundef


class TempVariableGenerator(object):

    """中間表現を生成する際に必要な一時変数を生成するクラス
       インスタンスとしてカウンタを持ち、メソッドとして新しい
       一時変数のdecl構造体を返すnewvardeclと、カウンタの値を0にリセットする
       resetを持つ"""

    def __init__(self):
        self.counter = 0

    def newvardecl(self):
        tempvar_name = "_t" + str(self.counter)
        tempvar_decl = sa.Decl(tempvar_name, 2, "temp", "int")
        self.counter += 1
        return tempvar_decl

    def reset(self):
        self.counter = 0
