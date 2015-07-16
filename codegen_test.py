#!/usr/bin/python
# -*- coding: utf-8 -*-

import nose
from unittest import TestCase
import semantic_analyzer as sa
import codegen

class LabelTest(TestCase):

    def setUp(self):
        self.labelman = codegen.LabelManager()

    def tearDown(self):
        pass

    def test_labelgen(self):
        """ラベル生成のテスト"""
        excepted_L0 = "L0"
        excepted_L1 = "L1"

        actual_L0 = self.labelman.nextlabel()
        actual_L1 = self.labelman.nextlabel()

        nose.tools.eq_(excepted_L0, actual_L0)
        nose.tools.eq_(excepted_L1, actual_L1)


class CodegenTest(TestCase):

    def setUp(self):
        self.code_generator = codegen.CodeGenerator([])

    def tearDown(self):
        pass

    def test_allocate_frame(self):
        """関数呼び出しの始めのフレーム確保のテスト"""
        expected = [codegen.Instruction("subu", ("$sp", "$sp", 24)),
                    codegen.Instruction("sw", ("$ra", "4($sp)")),
                    codegen.Instruction("sw", ("$fp", "0($sp)")),
                    codegen.Instruction("addiu", ("$fp", "$sp", 16))]

        actual = self.code_generator.allocate_frame(12, 4)

        nose.tools.ok_(expected == actual)

    def test_restore_frame(self):
        """関数呼び出しの終わりのフレーム復元のテスト"""
        expected = [codegen.Instruction("lw", ("$fp", "0($sp)")),]
                    codegen.Instruction("lw", ("$ra", "4($sp)")),
                    codegen.Instruction("addiu", ("$sp", "$sp", 24))

        actual = self.code_generator.restore_frame(12, 4)

        nose.tools.ok_(expected == actual)

    def test_varofs_to_fp(self):
        """局所変数のオフセットからアドレス式x$fpを生成するテスト"""
        expected_x = "-4($fp)"
        expected_y = "-8($fp)"

        vardecl_x = ic.VarDecl(sa.Decl("x", 2, "var", "int", -4))
        vardecl_y = ic.VarDecl(sa.Decl("y", 2, "var", "int", -8))
        actual_x = self.code_generator.varofs_to_fp(vardecl_x)
        actual_y = self.code_generator.varofs_to_fp(vardecl_y)

        nose.tools.eq_(expected_x, actual_x)
        nose.tools.eq_(expected_y, actual_y)

    def test_parammofs_to_fp(self):
        """パラメータのオフセットからアドレス式x($fp)を生成するテスト
           原理は局所変数と同じ"""
           expected = "4($fp)"

           paramdecl = ic.VarDecl(sa.Decl("x", 1, "param", "int", 4))
           actual = self.code_generator.varofs_to_fp(paramdecl)

           nose.tools.eq_(expected, actual)

    def test_argofs_to_fp(self):
        """引数のオフセットからアドレス式x($fp)を生成するテスト"""
        expected = "4($sp)"

        argdecl = ic.VarDecl(sa.Decl("_t0", 3, "temp", "int", 4))
        actual = self.code_generator.argofs_to_sp(argdecl)

        nose.tools.eq_(expected, actual)

    def test_intexp_to_code(self):
        """整数の中間表現をアセンブリに変換するテスト"""
        expected = [self.code_generator.Instruction()]



if __name__ == '__main__':
    nose.main(argv=['nose', '-v'])