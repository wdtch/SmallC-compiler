#!/usr/bin/python
# -*- coding: utf-8 -*-

import assign_address as a_addr
from unittest import TestCase
import nose
import semantic_analyzer as sa
import intermed_code as ic


class AssignAddrTest(TestCase):

    def setUp(self):
        self.assignaddr = a_addr.AssignAddress()

        self.vardecl_x = ic.VarDecl(sa.Decl("x", 2, "var", "int"))
        self.vardecl_y = ic.VarDecl(sa.Decl("y", 2, "var", "int"))

        self.paramdecl_x = ic.VarDecl(sa.Decl("x", 1, "param", "int"))
        self.paramdecl_y = ic.VarDecl(sa.Decl("y", 1, "param", "int"))

        self.globaldecl_x = ic.VarDecl(sa.Decl("gx", 0, "var", "int"))
        self.globaldecl_y = ic.VarDecl(sa.Decl("gy", 0, "var", "int"))

        self.arraydecl_x = ic.VarDecl(
            sa.Decl("ax", 2, "var", ("array", "int", 5)))  # ax[5]
        self.arraydecl_y = ic.VarDecl(
            sa.Decl("ay", 2, "var", ("array", "int", 5)))  # ay[5]

        self.arrayparam_x = ic.VarDecl(
            sa.Decl("ax", 1, "param", ("array", "int", 5)))  # ax[5]
        self.arrayparam_y = ic.VarDecl(
            sa.Decl("ay", 1, "param", ("array", "int", 3)))  # ay[5]

        self.globalarray_x = ic.VarDecl(
            sa.Decl("ax", 0, "var", ("array", "int", 5)))  # ax[5]
        self.globalarray_y = ic.VarDecl(
            sa.Decl("ay", 0, "var", ("array", "int", 5)))  # ay[5]

        # void f(int, int)
        self.decl_f = sa.Decl(
            "f", 0, "fun", ("fun", "void", "int", "int"), offset)

    def tearDown(self):
        pass

    def test_assign_vardecl_x(self):
        """局所変数xに対するアドレス割り当てテスト"""
        expected = -4

        self.vardecl_x.offset = self.assignaddr.ofs_to_var()
        currentofs = self.assignaddr.ofsman.current_offset

        nose.tools.ok_(expected == self.vardecl_x.offset == currentofs)

    def test_assign_verdecl_xy(self):
        """局所変数xとyに対するアドレス割り当てテスト"""
        expected_x = -4
        expected_y = -8

        self.vardecl_x.offset = self.assignaddr.ofs_to_var()
        self.vardecl_y.offset = self.assignaddr.ofs_to_var()
        currentofs = self.assignaddr.ofsman.current_offset

        nose.tools.eq_(expected_x, self.vardecl_x.offset)
        nose.tools.eq_(expected_y, self.vardecl_y.offset)
        nose.tools.eq_(expected_y, currentofs)

    def test_assign_param_x(self):
        """パラメータxに対するアドレス割り当てテスト"""
        expected = 4

        self.paramdecl_x.offset = self.assignaddr.ofs_to_param()
        currentofs = self.assignaddr.ofsman.current_offset

        nose.tools.ok_(expected == self.paramdecl_x.offset == currentofs)

    def test_assign_param_xy(self):
        """パラメータxとyに対するアドレス割り当てテスト"""
        expected_x = 4
        expected_y = 8

        self.paramdecl_x.offset = self.assignaddr.ofs_to_param()
        self.paramdecl_y.offset = self.assignaddr.ofs_to_param()
        currentofs = self.assignaddr.ofsman.current_offset

        nose.tools.eq_(expected_x, self.paramdecl_x.offset)
        nose.tools.eq_(expected_y, self.paramdecl_y.offset)
        nose.tools.eq_(expected_y, currentofs)

    def test_assign_globalvar_x(self):
        """グローバル変数xに対するアドレス割り当てテスト"""
        expected_x = -4

        self.globaldecl_x.offset = self.assignaddr.ofs_to_globalvar()
        currentofs = self.assignaddr.ofsman.current_offset

        nose.tools.eq_(expected_x, self.globaldecl_x.offset)
        nose.tools.eq_(expected_x, currentofs)

    def test_assign_globalvar_xy(self):
        """グローバル変数xとyに対するアドレス割り当てテスト"""
        expected_x = -4
        expected_y = -8

        self.globaldecl_x.offset = self.assignaddr.ofs_to_globalvar()
        self.globaldecl_y.offset = self.assignaddr.ofs_to_globalvar()
        currentofs = self.assignaddr.ofsman.current_offset

        nose.tools.eq_(expected_x, self.globaldecl_x.offset)
        nose.tools.eq_(expected_y, self.globaldecl_y.offset)
        nose.tools.eq_(expected_y, currentofs)

    def test_assign_array_x(self):
        """配列型局所変数ax[5]に対するアドレス割り当てテスト"""
        expected_x = -20

        self.arraydecl_x.offset = self.assignaddr.ofs_to_arrayvar(
            self.arraydecl_x.objtype[2])
        currentofs = self.assignaddr.ofsman.current_offset

        nose.tools.eq_(expected_x, self.arraydecl_x.offset)
        nose.tools.eq_(expected_x, currentofs)

    def test_assign_array_xy(self):
        """配列型局所変数ax[5]とay[3]に対するアドレス割り当てテスト"""
        expected_x = -20
        expected_y = -32

        self.arraydecl_x.offset = self.assignaddr.ofs_to_arrayvar(
            self.arraydecl_x.objtype[2])
        self.arraydecl_y.offset = self.assignaddr.ofs_to_arrayvar(
            self.arraydecl_y.objtype[2])
        currentofs = self.assignaddr.ofsman.current_offset

        nose.tools.eq_(expected_x, self.arraydecl_x.offset)
        nose.tools.eq_(expected_y, self.arraydecl_y.offset)
        nose.tools.eq_(expected_y, currentofs)

    def test_assign_varx_arrayx(self):
        """局所変数xと配列型局所変数ax[5]に対するアドレス割り当てテスト"""
        expected_x = -4
        expected_ax = -24

        self.vardecl_x.offset = self.assignaddr.ofs_to_var()
        self.arraydecl_x.offset = self.assignaddr.ofs_to_arrayvar(
            self.arraydecl_x.objtype[2])
        currentofs = self.assignaddr.ofsman.current_offset

        nose.tools.eq_(expected_x, self.vardecl_x.offset)
        nose.tools.eq_(expected_ax, self.arraydecl_x.offset)
        nose.tools.eq_(expected_ax, currentofs)

    def test_assign_param_array_x(self):
        """配列型パラメータax[5]に対するアドレス割り当てテスト"""
        expected_x = 20

        self.arrayparam_x.offset = self.assignaddr.ofs_to_arrayparam(
            self.arrayparam_x.objtype[2])
        currentofs = self.assignaddr.ofsman.current_offset

        nose.tools.eq_(expected_x, self.arrayparam_x.offset)
        nose.tools.eq_(expected_x, currentofs)

    def test_assign_array_xy(self):
        """配列型パラメータax[5]とay[3]に対するアドレス割り当てテスト"""
        expected_x = 20
        expected_y = 32

        self.arrayparam_x.offset = self.assignaddr.ofs_to_arrayparam(
            self.arrayparam_x.objtype[2])
        self.arrayparam_y.offset = self.assignaddr.ofs_to_arrayparam(
            self.arrayparam_y.objtype[2])
        currentofs = self.assignaddr.ofsman.current_offset

        nose.tools.eq_(expected_x, self.arrayparam_x.offset)
        nose.tools.eq_(expected_y, self.arrayparam_y.offset)
        nose.tools.eq_(expected_y, currentofs)

    def test_assign_varx_arrayx(self):
        """パラメータxと配列型パラメータax[5]に対するアドレス割り当てテスト"""
        expected_x = 4
        expected_ax = 24

        self.paramdecl_x.offset = self.assignaddr.ofs_to_param()
        self.arrayparam_x.offset = self.assignaddr.ofs_to_arrayparam(
            self.arrayparam_x.objtype[2])
        currentofs = self.assignaddr.ofsman.current_offset

        nose.tools.eq_(expected_x, self.paramdecl_x.offset)
        nose.tools.eq_(expected_ax, self.arrayparam_x.offset)
        nose.tools.eq_(expected_ax, currentofs)

    def test_assign_globalvar_x(self):
        """配列型グローバル変数ax[5]に対するアドレス割り当てテスト"""
        expected_x = -20

        self.globalarray_x.offset = self.assignaddr.ofs_to_globalarray()
        currentofs = self.assignaddr.ofsman.current_offset

        nose.tools.eq_(expected_x, self.globalarray_x.offset)
        nose.tools.eq_(expected_x, currentofs)

    def test_assign_globalvar_xy(self):
        """配列型グローバル変数ax[5]とグローバル変数yに対するアドレス割り当てテスト"""
        expected_x = -20
        expected_y = -24

        self.globalarray_x.offset = self.assignaddr.ofs_to_globalarray()
        self.globaldecl_y.offset = self.assignaddr.ofs_to_globalvar()
        currentofs = self.assignaddr.ofsman.current_offset

        nose.tools.eq_(expected_x, self.globalarray_x.offset)
        nose.tools.eq_(expected_y, self.globaldecl_y.offset)
        nose.tools.eq_(expected_y, currentofs)

    def test_compstmt1(self):
        """void f(int x, int y) {...}に対するアドレス割り当てテスト"""
        expected_ofsx = 4
        expected_ofsy = 8

        expected_x = ic.VarDecl(sa.Decl("x", 1, "param", "int", expected_ofsx))
        expected_y = ic.VarDecl(sa.Decl("x", 1, "param", "int", expected_ofsy))

        params = [self.paramdecl_x, self.paramdecl_y]
        intermed_f = sa.Decl("f", 0, "fun", ("fun", "void", "int", "int"))
        decls = []
        stmts = []
        body = ic.CompoundStatement(decls, stmts)
        fundef_f = ic.FunctionDefinition(intermed_f, params, body)

        self.assignaddr.intermed_code = [fundef_f]
        result = self.assignaddr.assign_address()

        nose.tools.eq_(result[0].params, [expected_x, expected_y])

    def test_compstmt2(self):
        """void f(int x, int y) {int x; int y; ...}に対するアドレス割り当てテスト"""
        expected_ofs_paramx = 4
        expected_ofs_paramy = 8
        expected_ofs_varx = -4
        expected_ofs_vary = -8

        expected_varx = ic.VarDecl(
            sa.Decl("x", 2, "var", "int", expected_ofs_varx))
        expected_vary = ic.VarDecl(
            sa.Decl("y", 2, "var", "int", expected_ofs_vary))

        expected_paramx = ic.VarDecl(
            sa.Decl("x", 1, "param", "int", expected_ofs_paramx))
        expected_paramy = ic.VarDecl(
            sa.Decl("x", 1, "param", "int", expected_ofs_paramy))

        params = [self.paramdecl_x, self.paramdecl_y]
        intermed_f = sa.Decl("f", 0, "fun", ("fun", "void", "int", "int"))
        decls = [self.vardecl_x, self.vardecl_y]
        stmts = []
        body = ic.CompoundStatement(decls, stmts)
        fundef_f = ic.FunctionDefinition(intermed_f, params, body)

        self.assignaddr.intermed_code = [fundef_f]
        result = self.assignaddr.assign_address()

        nose.tools.eq_(result[0].params, [expected_paramx, expected_paramy])
        nose.tools.eq_(
            result[0].body.decls, [expected_varx, expected_vary])

    def test_compstmt3(self):
        """int gx; int gy; void f(int x, int y) {int x; int y; ...}に対するアドレス割り当てテスト"""
        expected_ofs_globalx = -4
        expected_ofs_globaly = -8
        expected_ofs_paramx = 4
        expected_ofs_paramy = 8
        expected_ofs_varx = -4
        expected_ofs_vary = -8

        expected_globalx = ic.VarDecl(
            sa.Decl("gx", 0, "var", "int", expected_ofs_globalx))
        expected_globaly = ic.VarDecl(
            sa.Decl("gy", 0, "var", "int", expected_ofs_globaly))

        expected_varx = ic.VarDecl(
            sa.Decl("x", 2, "var", "int", expected_ofs_varx))
        expected_vary = ic.VarDecl(
            sa.Decl("y", 2, "var", "int", expected_ofs_vary))

        expected_paramx = ic.VarDecl(
            sa.Decl("x", 1, "param", "int", expected_ofs_paramx))
        expected_paramy = ic.VarDecl(
            sa.Decl("x", 1, "param", "int", expected_ofs_paramy))

        params = [self.paramdecl_x, self.paramdecl_y]
        intermed_f = sa.Decl("f", 0, "fun", ("fun", "void", "int", "int"))
        decls = [self.vardecl_x, self.vardecl_y]
        stmts = []
        body = ic.CompoundStatement(decls, stmts)
        fundef_f = ic.FunctionDefinition(intermed_f, params, body)

        exterenal_dec = [self.globaldecl_x, self.globaldecl_y, fundef_f]
        self.assignaddr.intermed_code = exterenal_dec
        result = self.assignaddr.assign_address()

        nose.tools.eq_(result[0], expected_globalx)
        nose.tools.eq_(result[1], expected_globaly)
        nose.tools.eq_(result[2].params, [expected_paramx, expected_paramy])
        nose.tools.eq_(
            result[2].body.decls, [expected_varx, expected_vary])
