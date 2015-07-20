#!/usr/bin/python
# -*- coding: utf-8 -*-

from unittest import TestCase
import nose
from itertools import izip
import intermed_code as ic
import ast
import semantic_analyzer as sa

# テスト


class TempVarTest(TestCase):

    def setUp(self):
        self.tvg = ic.TempVariableGenerator()

    def tearDown(self):
        pass

    def test_tempvardecl(self):
        """一時変数のDecl構造体生成のテスト"""
        expected = sa.Decl("_t0", 0, "temp", "int")
        actual = self.tvg.newvardecl()
        nose.tools.eq_(expected, actual)

        expected = sa.Decl("_t1", 0, "temp", "int")
        actual = self.tvg.newvardecl()
        nose.tools.eq_(expected, actual)

        expected = sa.Decl("_t2", 0, "temp", "int")
        actual = self.tvg.newvardecl()
        nose.tools.ok_(expected == actual)


class IntermedCodeTest(TestCase):

    def setUp(self):
        self.icg = ic.IntermedCodeGenerator(ast.NullNode())  # とりあえずnull
        self.decl_x = sa.Decl("x", 0, "var", "int")
        self.decl_y = sa.Decl("y", 0, "var", "int")
        self.decl_temp0 = sa.Decl("_t0", 0, "temp", "int")
        self.decl_temp1 = sa.Decl("_t1", 0, "temp", "int")
        self.decl_temp2 = sa.Decl("_t2", 0, "temp", "int")

    def tearDown(self):
        pass

    def test_num(self):
        """1の中間表現生成テスト"""
        intermed_1 = ic.IntExpression(1)
        expected = [ic.LetStatement("x", intermed_1)]

        ast_1 = ast.Number(1)
        # icg.ast_node = ast_1
        actual = self.icg.intermed_code_exp("x", ast_1)

        nose.tools.ok_(expected == actual)

    def test_var(self):
        """xの中間表現生成テスト"""
        intermed_varx = ic.VarExpression(self.decl_x)
        expected = [ic.LetStatement("y", intermed_varx)]

        ast_x = ast.Identifier(self.decl_x, 1)
        actual = self.icg.intermed_code_exp("y", ast_x)

        nose.tools.ok_(expected == actual)
        # nose.tools.ok_(False, msg="あかんやつテスト")

    def test_var_pointer(self):
        """x(ポインタ型)の中間表現生成テスト"""
        decl_x_p = sa.Decl("x", 0, "var", ("pointer", "int"))
        intermed_varx_p = ic.VarExpression(decl_x_p)
        expected = [ic.LetStatement("y", intermed_varx_p)]

        ast_x_p = ast.Pointer(ast.Identifier(decl_x_p, 1))
        actual = self.icg.intermed_code_exp("y", ast_x_p)

        nose.tools.ok_(expected == actual)

    def test_aopexp_plus(self):
        """2 + 3の中間表現生成テスト"""
        intermed_2 = ic.LetStatement(self.decl_temp0, ic.IntExpression(2))
        intermed_3 = ic.LetStatement(self.decl_temp1, ic.IntExpression(3))
        aop_2plus3 = ic.ArithmeticOperation(
            "PLUS", self.decl_temp0, self.decl_temp1)
        expected = [intermed_2, intermed_3, ic.LetStatement("x", aop_2plus3)]

        ast_2 = ast.Number(2)
        ast_3 = ast.Number(3)
        actual = self.icg.intermed_code_exp(
            "x", ast.BinaryOperators("PLUS", ast_2, ast_3))

        nose.tools.ok_(expected == actual)

    def test_aopexp_pointer1(self):
        """p(pointer) + 1の中間表現生成テスト"""
        decl_p = sa.Decl("p", 0, "var", ("pointer", "int"))
        intermed_p = ic.LetStatement(self.decl_temp0, ic.VarExpression(decl_p))
        intermed_1 = ic.LetStatement(self.decl_temp1, ic.IntExpression(1))
        intermed_4 = ic.LetStatement(self.decl_temp2, ic.IntExpression(4))
        intermed_1times4 = ic.ArithmeticOperation(
            "TIMES", self.decl_temp1, self.decl_temp2)
        aop_pplus1 = ic.ArithmeticOperation(
            "PLUS", self.decl_temp0, intermed_1times4)
        expected = [intermed_p, intermed_1, intermed_4,
                    ic.LetStatement("x", aop_pplus1)]

        ast_p = ast.Pointer(ast.Identifier(decl_p, 1))
        ast_1 = ast.Number(1)
        actual = self.icg.intermed_code_exp(
            "x", ast.BinaryOperators("PLUS", ast_p, ast_1))

        nose.tools.ok_(expected == actual)

    def test_aopexp_pointer2(self):
        """1 + p(pointer)の中間表現生成テスト"""
        decl_p = sa.Decl("p", 0, "var", ("pointer", "int"))
        intermed_1 = ic.LetStatement(self.decl_temp0, ic.IntExpression(1))
        intermed_p = ic.LetStatement(self.decl_temp1, ic.VarExpression(decl_p))
        intermed_4 = ic.LetStatement(self.decl_temp2, ic.IntExpression(4))
        intermed_1times4 = ic.ArithmeticOperation(
            "TIMES", self.decl_temp0, self.decl_temp2)
        aop_pplus1 = ic.ArithmeticOperation(
            "PLUS", intermed_1times4, self.decl_temp1)
        expected = [intermed_1, intermed_p, intermed_4,
                    ic.LetStatement("x", aop_pplus1)]

        ast_p = ast.Pointer(ast.Identifier(decl_p, 1))
        ast_1 = ast.Number(1)
        actual = self.icg.intermed_code_exp(
            "x", ast.BinaryOperators("PLUS", ast_1, ast_p))

        nose.tools.ok_(expected == actual)

    def test_relopexp_le(self):
        """3 <= 2の中間表現生成テスト"""
        intermed_2 = ic. LetStatement(self.decl_temp0, ic.IntExpression(2))
        intermed_3 = ic.LetStatement(self.decl_temp1, ic.IntExpression(3))
        relop_2le3 = ic.RelationalExpression(
            "LEQ", self.decl_temp0, self.decl_temp1)
        expected = [intermed_2, intermed_3, ic.LetStatement("x", relop_2le3)]

        ast_2 = ast.Number(2)
        ast_3 = ast.Number(3)
        actual = self.icg.intermed_code_exp(
            "x", ast.BinaryOperators("LEQ", ast_2, ast_3))

        nose.tools.ok_(expected == actual)

    def test_addrexp(self):  # わからん
        """アドレス取得(&y)の中間表現テスト"""
        decl_y_p = sa.Decl("y", 0, "var", ("pointer", "int"))
        # intermed_varyp = ic.VarExpression(decl_y_p)
        intermed_addr_yp = ic.AddressExpression(decl_y_p)
        expected = [ic.LetStatement("x", intermed_addr_yp)]

        id_y = ast.Identifier(decl_y_p, 1)  # decl?
        ast_y_p = ast.Address(id_y)
        actual = self.icg.intermed_code_exp("x", ast_y_p)

        nose.tools.ok_(expected == actual)

    def test_emptystmt(self):
        """空文( ; )の中間表現テスト"""
        intermed_empty = ic.EmptyStatement()
        expected = [intermed_empty]

        actual = self.icg.intermed_code_statement(ast.NullNode())

        nose.tools.ok_(expected == actual)

    def test_letstmt(self):
        """x = 2;の中間表現テスト"""
        intermed_2 = ic.IntExpression(2)
        intermed_let = ic.LetStatement(self.decl_x, intermed_2)
        expected = [intermed_let]

        ast_x = ast.Identifier(self.decl_x, 1)  # ほんまか？Decl？
        ast_2 = ast.Number(2)
        actual = self.icg.intermed_code_statement(
            ast.BinaryOperators("ASSIGN", ast_x, ast_2))

        nose.tools.ok_(expected == actual)

    def test_writestmt(self):  # わからん
        """*x = 1;の中間表現テスト"""
        decl_x_p = sa.Decl("x", 0, "var", ("pointer", "int"))
        varexp_x_p = ic.VarExpression(decl_x_p)
        intermed_1 = ic.IntExpression(1)
        let_x_p = ic.LetStatement(self.decl_temp0, varexp_x_p)
        let_1 = ic.LetStatement(self.decl_temp1, intermed_1)
        intermed_write = ic.WriteStatement(self.decl_temp0, self.decl_temp1)
        expected = [let_x_p, let_1, intermed_write]

        ast_x = ast.Identifier(decl_x_p, 1)  # ほんまか？Decl？
        ast_x_p = ast.Pointer(ast_x)
        ast_1 = ast.Number(1)
        actual = self.icg.intermed_code_statement(
            ast.BinaryOperators("ASSIGN", ast_x_p, ast_1))

        nose.tools.ok_(expected == actual)

    def test_readstmt(self):  # わからん
        """x = *y;の中間表現テスト"""
        varexp_x = ic.VarExpression(self.decl_x)
        let_x = ic.LetStatement(self.decl_temp0, varexp_x)
        decl_y_p = sa.Decl("y", 0, "var", ("pointer", "int"))
        varexp_y_p = ic.VarExpression(decl_y_p)
        let_y_p = ic.LetStatement(self.decl_temp1, varexp_y_p)
        intermed_read = ic.ReadStatement(
            self.decl_temp0, self.decl_temp1)  # *yに対応するself.decl_y?
        expected = [let_x, let_y_p, intermed_read]

        ast_x = ast.Identifier(self.decl_x, 1)  # Decl?
        ast_y = ast.Identifier(decl_y_p, 2)  # Decl?
        ast_y_p = ast.Pointer(ast_y)
        actual = self.icg.intermed_code_statement(
            ast.BinaryOperators("ASSIGN", ast_x, ast_y_p))

        nose.tools.ok_(expected == actual)

    def test_ifstmt(self):
        """if (x) { ;} else { ;}の中間表現テスト"""
        varexp_x = ic.VarExpression(self.decl_x)
        let_x = ic.LetStatement(self.decl_temp0, varexp_x)
        intermed_emptystmt = [ic.EmptyStatement()]
        emptycompstmt = ic.CompoundStatement([], intermed_emptystmt)
        intermed_if = ic.IfStatement(
            self.decl_temp0, emptycompstmt, emptycompstmt)
        expected = [let_x, intermed_if]

        ast_x = ast.Identifier(self.decl_x, 1)
        nulldec_list = ast.DeclarationList(ast.NullNode())
        nullstmt_list = ast.StatementList(ast.NullNode())
        then_stmt = ast.CompoundStatement(nulldec_list, nullstmt_list)
        else_stmt = ast.CompoundStatement(nulldec_list, nullstmt_list)
        ast_if = ast.IfStatement(ast_x, then_stmt, else_stmt)
        actual = self.icg.intermed_code_statement(ast_if)

        nose.tools.ok_(expected == actual)

    def test_whilestmt(self):
        """while (x) { ;}の中間表現テスト"""
        varexp_x = ic.VarExpression(self.decl_x)
        let_x = ic.LetStatement(self.decl_temp0, varexp_x)
        intermed_emptystmt = [ic.EmptyStatement()]
        emptycompstmt = ic.CompoundStatement([], intermed_emptystmt)
        intermed_while = ic.WhileStatement(self.decl_temp0, emptycompstmt)
        expected = [let_x, intermed_while]

        ast_x = ast.Identifier(self.decl_x, 1)
        nulldec_list = ast.DeclarationList(ast.NullNode())
        nullstmt_list = ast.StatementList(ast.NullNode())
        while_stmt = ast.CompoundStatement(nulldec_list, nullstmt_list)
        ast_while = ast.WhileLoop(ast_x, while_stmt)
        actual = self.icg.intermed_code_statement(ast_while)

        nose.tools.ok_(expected == actual)

    def test_callstmt_int(self):
        """dest = f(x, 3);の中間表現テスト(f:int)"""
        varexp_x = ic.VarExpression(self.decl_x)
        intermed_3 = ic.IntExpression(3)
        let_3 = ic.LetStatement(self.decl_temp1, intermed_3)
        let_x = ic.LetStatement(self.decl_temp0, varexp_x)
        intermed_args_list = [self.decl_temp0, self.decl_temp1]
        decl_dest = sa.Decl("dest", 0, "var", "int")
        decl_f = sa.Decl("f", 0, "fun", ("fun", "int", "int", "int"))
        intermed_funccall = ic.CallStatement(
            decl_dest, decl_f, intermed_args_list)
        expected = [let_3, let_x, intermed_funccall]

        decl_dest = sa.Decl("dest", 0, "var", "int")
        ast_x = ast.Identifier(self.decl_x, 1)
        ast_3 = ast.Number(3)
        ast_args_list = [ast_x, ast_3]
        callexp_f = ast.FunctionExpression(decl_f, ast_args_list, 1)
        ast_dest = ast.Identifier(decl_dest, 1)
        ast_assign = ast.BinaryOperators("ASSIGN", ast_dest, callexp_f)
        actual = self.icg.intermed_code_statement(ast_assign)

        nose.tools.ok_(expected == actual)

    def test_callstmt_void(self):
        """f(x, 3);の中間表現テスト(f:void)"""
        varexp_x = ic.VarExpression(self.decl_x)
        intermed_3 = ic.IntExpression(3)
        let_3 = ic.LetStatement(self.decl_temp1, intermed_3)
        let_x = ic.LetStatement(self.decl_temp0, varexp_x)
        args_list = [self.decl_temp0, self.decl_temp1]
        decl_f = sa.Decl("f", 0, "fun", ("fun", "void", "int", "int"))
        intermed_funccall = ic.CallStatement(None, decl_f, args_list)
        expected = [let_3, let_x, intermed_funccall]

        ast_x = ast.Identifier(self.decl_x, 1)
        ast_3 = ast.Number(3)
        ast_args_list = ast.ArgumentExpressionList(ast_x)
        ast_args_list.append(ast_3)
        callexp_f = ast.FunctionExpression(decl_f, ast_args_list, 1)
        actual = self.icg.intermed_code_statement(callexp_f)

        nose.tools.ok_(expected == actual)

    def test_returnstmt(self):
        """return 3;の中間表現テスト"""
        intermed_3 = ic.IntExpression(3)
        let_3 = ic.LetStatement(self.decl_temp0, intermed_3)
        return_3 = ic.ReturnStatement(self.decl_temp0)
        expected = [let_3, return_3]

        ast_3 = ast.Number(3)
        ast_return = ast.ReturnStatement(ast_3)
        actual = self.icg.intermed_code_statement(ast_return)

        nose.tools.ok_(expected == actual)

    def test_printstmt(self):
        """print(3);の中間表現テスト"""
        intermed_2 = ic.IntExpression(2)
        let_2 = ic.LetStatement(self.decl_temp0, intermed_2)
        intermed_print = ic.PrintStatement(self.decl_temp0)
        expected = [let_2, intermed_print]

        ast_2 = ast.Number(2)
        args_list = ast.ArgumentExpressionList(ast_2)
        decl_print = sa.Decl("print", 0, "fun", ("fun", "void", "int"))
        ast_print = ast.FunctionExpression(decl_print, args_list, 1)
        actual = self.icg.intermed_code_statement(ast_print)

        nose.tools.ok_(expected == actual)

    def test_vardecl(self):
        """int x;の中間表現テスト"""
        intermed_decl_x = ic.VarDecl(self.decl_x)
        expected = [intermed_decl_x]

        ast_x = ast.Identifier(self.decl_x, 1)
        direct_declarator = ast.DirectDeclarator(ast_x)
        declarator = ast.Declarator("NORMAL", direct_declarator)
        declarator_list = ast.DeclaratorList(declarator)
        type_spcf = ast.TypeSpecifier("int")
        declaration = ast.Declaration(type_spcf, declarator_list)
        actual = self.icg.intermed_code_vardecl(declaration)

        nose.tools.ok_(expected == actual)

    def test_compstmt(self):
        """int x; int y; x = 0; y = 1;の中間表現テスト"""
        intermed_decl_x = ic.VarDecl(self.decl_x)
        intermed_decl_y = ic.VarDecl(self.decl_y)

        intermed_0 = ic.IntExpression(0)
        intermed_letx0 = ic.LetStatement(self.decl_x, intermed_0)

        intermed_1 = ic.IntExpression(1)
        intermed_lety1 = ic.LetStatement(self.decl_y, intermed_1)

        intermed_decls = [intermed_decl_x, intermed_decl_y]
        intermed_stmts = [intermed_letx0, intermed_lety1]
        expected = [ic.CompoundStatement(intermed_decls, intermed_stmts)]

        ast_x = ast.Identifier(self.decl_x, 1)
        directd_x = ast.DirectDeclarator(ast_x)
        declarator_x = ast.Declarator("NORMAL", directd_x)
        decllist_x = ast.DeclaratorList(declarator_x)
        type_spcf = ast.TypeSpecifier("int")
        declaration_x = ast.Declaration(type_spcf, decllist_x)

        ast_y = ast.Identifier(self.decl_y, 2)
        directd_y = ast.DirectDeclarator(ast_y)
        declarator_y = ast.Declarator("NORMAL", directd_y)
        decllist_y = ast.DeclaratorList(declarator_y)
        declaration_y = ast.Declaration(type_spcf, decllist_y)

        ast_0 = ast.Number(0)
        assign_x0 = ast.BinaryOperators("ASSIGN", ast_x, ast_0)

        ast_1 = ast.Number(1)
        assign_y1 = ast.BinaryOperators("ASSIGN", ast_y, ast_1)

        decls = ast.DeclarationList(declaration_x)
        decls.append(declaration_y)

        stmts = ast.StatementList(assign_x0)
        stmts.append(assign_y1)

        compstmts = ast.CompoundStatement(decls, stmts)

        actual = self.icg.intermed_code_statement(compstmts)

        nose.tools.ok_(expected == actual)

    def test_compstmt_temp(self):
        """int x; int y; x = 0; y = 1; return x+y;の中間表現テスト"""
        intermed_decl_x = ic.VarDecl(self.decl_x)
        intermed_decl_y = ic.VarDecl(self.decl_y)
        intermed_0 = ic.IntExpression(0)
        intermed_letx0 = ic.LetStatement(self.decl_x, intermed_0)
        intermed_1 = ic.IntExpression(1)
        intermed_lety1 = ic.LetStatement(self.decl_y, intermed_1)

        intermed_x = ic.VarExpression(self.decl_x)
        intermed_y = ic.VarExpression(self.decl_y)
        intermed_temp_x = ic.LetStatement(self.decl_temp1, intermed_x)
        intermed_temp_y = ic.LetStatement(self.decl_temp2, intermed_y)
        intermed_xplusy = ic.LetStatement(self.decl_temp0, ic.ArithmeticOperation(
            "PLUS", self.decl_temp1, self.decl_temp2))
        intermed_return = ic.ReturnStatement(self.decl_temp0)

        intermed_decl_temp0 = ic.VarDecl(self.decl_temp0)
        intermed_decl_temp1 = ic.VarDecl(self.decl_temp1)
        intermed_decl_temp2 = ic.VarDecl(self.decl_temp2)

        intermed_decls = [intermed_decl_x, intermed_decl_y,
                          intermed_decl_temp1, intermed_decl_temp2, intermed_decl_temp0]
        intermed_stmts = [intermed_letx0, intermed_lety1, intermed_temp_x,
                          intermed_temp_y, intermed_xplusy, intermed_return]

        expected = [ic.CompoundStatement(intermed_decls, intermed_stmts)]

        ast_x = ast.Identifier(self.decl_x, 1)
        directd_x = ast.DirectDeclarator(ast_x)
        declarator_x = ast.Declarator("NORMAL", directd_x)
        decllist_x = ast.DeclaratorList(declarator_x)
        type_spcf = ast.TypeSpecifier("int")
        declaration_x = ast.Declaration(type_spcf, decllist_x)

        ast_y = ast.Identifier(self.decl_y, 2)
        directd_y = ast.DirectDeclarator(ast_y)
        declarator_y = ast.Declarator("NORMAL", directd_y)
        decllist_y = ast.DeclaratorList(declarator_y)
        declaration_y = ast.Declaration(type_spcf, decllist_y)

        decls = ast.DeclarationList(declaration_x)
        decls.append(declaration_y)

        ast_0 = ast.Number(0)
        assign_x0 = ast.BinaryOperators("ASSIGN", ast_x, ast_0)

        ast_1 = ast.Number(1)
        assign_y1 = ast.BinaryOperators("ASSIGN", ast_y, ast_1)

        ast_xplusy = ast.BinaryOperators("PLUS", ast_x, ast_y)
        ast_return = ast.ReturnStatement(ast_xplusy)

        stmts = ast.StatementList(assign_x0)
        stmts.append(assign_y1)
        stmts.append(ast_return)

        compstmts = ast.CompoundStatement(decls, stmts)

        actual = self.icg.intermed_code_statement(compstmts)

        nose.tools.ok_(expected == actual)

    def test_fundef(self):
        """int ret_i(int i) {return i;}の中間表現テスト"""
        funcdecl = sa.Decl("ret_i", 0, "fun", ("fun", "int", "int"))

        decl_i = sa.Decl("i", 1, "param", "int")
        param_list = [ic.VarDecl(decl_i)]

        intermed_i = ic.VarExpression(decl_i)
        intermed_temp_i = ic.LetStatement(self.decl_temp0, intermed_i)
        intermed_return = ic.ReturnStatement(self.decl_temp0)

        intermed_decls = [ic.VarDecl(self.decl_temp0)]
        intermed_stmts = [intermed_temp_i, intermed_return]
        intermed_compstmt = ic.CompoundStatement(intermed_decls, intermed_stmts)

        intermed_fundef = ic.FunctionDefinition(funcdecl, param_list, intermed_compstmt)

        expected = intermed_fundef

        ast_i = ast.Identifier(decl_i, 1)
        ast_return = ast.ReturnStatement(ast_i)
        ast_stmtlist = ast.StatementList(ast_return)
        ast_decllist = ast.DeclarationList(ast.NullNode())
        ast_compstmt = ast.CompoundStatement(ast_decllist, ast_stmtlist)

        typespcf = ast.TypeSpecifier("int")
        id_i = ast.Identifier(decl_i, 1)
        param_declarator = ast.ParameterDeclarator("NORMAL", id_i)
        param_declaration = ast.ParameterDeclaration(typespcf, param_declarator)
        paramdec = ast.ParameterDeclaration(typespcf, param_declarator)
        param_typelist = ast.ParameterTypeList(param_declaration)

        func_declarator = ast.FunctionDeclarator("NORMAL", ast.Identifier(funcdecl, 10), param_typelist)
        fundef = ast.FunctionDefinition(typespcf, func_declarator, ast_compstmt)

        actual = self.icg.intermed_code_fundef(fundef)

        nose.tools.ok_(expected == actual)


if __name__ == '__main__':
    nose.main(argv=['nose', '-v'])
