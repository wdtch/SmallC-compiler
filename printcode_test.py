#!/usr/bin/python
# -*- coding: utf-8 -*-

import nose
from unittest import TestCase
import codegen
import printcode


class PrintCodeTest(TestCase):

    def setUp(self):
        self.printer = printcode.PrintCode([])

    def tearDown(self):
        pass

    def test_instr(self):
        """Instruction型のインスタンスを文字列に変換するテスト"""
        expected = "    li $t0,0\n"

        instr = codegen.Instruction("li", ("$t0", 0))
        actual = self.printer.struct_to_string(instr)

        nose.tools.eq_(expected, actual)

    def test_label(self):
        """Label型のインスタンスを文字列に変換するテスト"""
        expected = 1"main:\n"

        label = codegen.Label("main")
        actual = self.printer.struct_to_string(label)

        nose.tools.eq_(expected, actual)

    def test_code_to_string1(self):
        """アセンブリのリストを文字列に変換するテスト(Instructionのみ)"""
        expected = "    .data\n" + "nl: .asciiz \"\\n\"\n" + \
                   "    li $t0,0\n" + \
                   "    li $t1,1\n"

        code = [codegen.Instruction("li", ("$t0", 0)),
                codegen.Instruction("li", ("$t1", 1))]
        self.printer.code = code
        actual = self.printer.code_to_string()

        nose.tools.eq_(expected, actual)

    def test_code_to_string2(self):
        """アセンブリのリストを文字列に変換するテスト(Instructions, Label)"""
        expected = "    .data\n" + "nl: .asciiz \"\\n\"\n" + "main:\n" + "    li $t0,0\n"

        code = [codegen.Label("main"),
                codegen.Instruction("li", ("$t0", 0))]
        self.printer.code = code
        actual = self.printer.code_to_string()

        nose.tools.eq_(expected, actual)

if __name__ == '__main__':
    nose.main(argv=['nose', '-v'])