#!/usr/bin/python
# -*- coding: utf-8 -*-

import nose
from unittest import TestCase
import collections
import semantic_analyzer as sa
import intermed_code as ic
import codegen

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
        expected = [codegen.Instruction("lw", ("$fp", "0($sp)")),
                    codegen.Instruction("lw", ("$ra", "4($sp)")),
                    codegen.Instruction("addiu", ("$sp", "$sp", 24)),
                    codegen.Instruction("jr", ("$ra"))]

        actual = self.code_generator.restore_frame(12, 4)

        nose.tools.ok_(expected == actual)

    def test_varofs_to_fp(self):
        """局所変数のオフセットからアドレス式x($fp)を生成するテスト"""
        expected_x = "-4($fp)"
        expected_y = "-8($fp)"

        vardecl_x = ic.VarDecl(sa.Decl("x", 2, "var", "int", -4))
        vardecl_y = ic.VarDecl(sa.Decl("y", 2, "var", "int", -8))
        actual_x = self.code_generator.varofs_to_fp(vardecl_x.var)
        actual_y = self.code_generator.varofs_to_fp(vardecl_y.var)

        nose.tools.eq_(expected_x, actual_x)
        nose.tools.eq_(expected_y, actual_y)

    def test_parammofs_to_fp(self):
        """パラメータのオフセットからアドレス式x($fp)を生成するテスト
           原理は局所変数と同じ"""
        expected = "4($fp)"

        paramdecl = ic.VarDecl(sa.Decl("x", 1, "param", "int", 4))
        actual = self.code_generator.varofs_to_fp(paramdecl.var)

        nose.tools.eq_(expected, actual)

    def test_argofs_to_fp(self):
        """引数のオフセットからアドレス式x($sp)を生成するテスト"""
        expected = "4($sp)"

        argdecl = ic.VarDecl(sa.Decl("_t0", 3, "temp", "int", 4))
        actual = self.code_generator.argofs_to_sp(argdecl.var)

        nose.tools.eq_(expected, actual)

    def test_intexp_to_code(self):
        """整数8の中間表現をアセンブリに変換するテスト"""
        expected = [codegen.Instruction("li", ("$t0", 8)),
                    codegen.Instruction("sw", ("$t0", "-4($fp)"))]

        destvar = sa.Decl("x", 2, "var", "int", -4)
        intexp = ic.IntExpression(8)
        actual = self.code_generator.intermed_exp_to_code(destvar, intexp)

        nose.tools.ok_(expected == actual)

    def test_varexp_to_code(self):
        """変数xの中間表現をアセンブリに変換するテスト"""
        expected = [codegen.Instruction("lw", ("$t0", "-8($fp)")),
                    codegen.Instruction("sw", ("$t0", "-4($fp)"))]

        destvar = sa.Decl("_t0", 2, "var", "int", -4)
        varexp = ic.VarExpression(sa.Decl("x", 2, "var", "int", -8))
        actual = self.code_generator.intermed_exp_to_code(destvar, varexp)

        nose.tools.ok_(expected == actual)

    # def test_pointer_to_code(self):
    #     """ポインタ型変数*xの中間表現をアセンブリに変換するテスト""" # readstmt?
    #     expected = [codegen.Instruction("lw", ("$t0", "-4($fp)")),
    #                 codegen.Instruction("lw", ("$t0", "0($t0)")),
    #                 codegen.Instruction("sw", ("$t0", "-12($fp)"))]  #

    #     destvar = sa.Decl("_t0", 2, "var", "int", -12)
    #     pointerexp = ic.VarExpression(
    #         sa.Decl("x", 2, "var", ("pointer", "int"), -4))
    #     actual = self.code_generator.intermed_exp_to_code(destvar, pointerexp)

    #     nose.tools.ok_(expected == actual)

    def test_address_to_code(self):
        """アドレス取得&xの中間表現をアセンブリに変換するテスト"""
        expected = [codegen.Instruction("la", ("$t0", "0($fp)")),
                    codegen.Instruction("sw", ("$t0", "-4($fp)"))]

        x = sa.Decl("x", 2, "var", "int", 0)
        dest = sa.Decl("_t0", 2, "temp", "int", -4)
        addrexp = ic.AddressExpression(x)
        actual = self.code_generator.intermed_exp_to_code(dest, addrexp)

        nose.tools.ok_(expected == actual)

    def test_arrayexp_to_code(self):
        """配列アクセスの中間表現(int a[5]に対してx=a[3])をアセンブリに変換するテスト"""
        expected = [codegen.Instruction("la", ("$t0", "-16($fp)")),  # $t0に配列の先頭アドレス(ここでいいのか？)
                    codegen.Instruction("sw", ("$t0", "-24($fp)")),  # _t0の場所に格納
                    # Int(3)
                    codegen.Instruction("li", ("$t0", 3)), # 3をロード
                    codegen.Instruction("sw", ("$t0", "-28($fp)")), # _t1の場所に格納
                    # Int(4)
                    codegen.Instruction("li", ("$t0", 4)), # 4をロード
                    codegen.Instruction("sw", ("$t0", "-32($fp)")), # _t2の場所に格納
                    # aop(3*4)
                    codegen.Instruction("lw", ("$t0", "-28($fp)")), # 3*4のオペランドをロード
                    codegen.Instruction("lw", ("$t1", "-32($fp)")),
                    codegen.Instruction("mul", ("$t0", "$t0", "$t1")),  # $t0に3*4
                    # aop(p+(3*4))
                    codegen.Instruction("lw", ("$t1", "-24($fp)")), # 配列のアドレスを$t1に($t0は使用中)
                    codegen.Instruction("add", ("$t0", "$t0", "$t1")),  # t0 = a + (4*3)
                    codegen.Instruction("lw", ("$t0", "0($t0)")),
                    # x(dest) = aop(p + 3*4)
                    codegen.Instruction("sw", ("$t0", "-20($fp)"))]

        destvar = sa.Decl("x", 2, "var", "int", -20)
        array = sa.Decl("a", 2, "var", ("array", "int", 5), -16)
        temp0 = sa.Decl("_t0", 2, "temp", "int", -24)
        temp1 = sa.Decl("_t1", 2, "temp", "int", -28)
        temp2 = sa.Decl("_t2", 2, "temp", "int", -32)

        nose.tools.ok_(expected == actual)

    def test_emptystatement_to_code(self):
        """空文の中間表現をアセンブリに変換するテスト"""
        expected = [codegen.Instruction("nop", ())]
        actual = self.code_generator.intermed_stmt_to_code(0, 0, ic.EmptyStatement())

        nose.tools.ok_(expected == actual)

    def test_letstatement_to_code(self):
        """x = 1;の中間表現をアセンブリに変換するテスト"""
        expected = [codegen.Instruction("li", ("$t0", 1)),
                    codegen.Instruction("sw", ("$t0", "-4($fp)"))]

        intermed_1 = ic.IntExpression(1)
        dest_x = sa.Decl("x", 2, "var", "int", -4)
        intermed_let = ic.LetStatement(dest_x, intermed_1)
        actual = self.code_generator.intermed_stmt_to_code(4, 0, intermed_let)

        nose.tools.ok_(expected == actual)

    def test_printstmt_to_code(self):
        """print(x);(xのオフセットは-4)の中間表現をアセンブリに変換するテスト"""
        expected = [codegen.Instruction("li", ("$v0", 1)),
                    codegen.Instruction("lw", ("$t0", "-4($fp)")),
                    codegen.Instruction("move", ("$a0", "$t0")),
                    codegen.Instruction("syscall", ()),
                    codegen.Instruction("li", ("$v0", 4)),
                    codegen.Instruction("la", ("$a0", "nl")),
                    codegen.Instruction("syscall", ())]

        x = sa.Decl("x", 2, "var", "int", -4)
        intermed_print = ic.PrintStatement(x)
        actual = self.code_generator.intermed_stmt_to_code(4, 0, intermed_print)

        nose.tools.ok_(expected == actual)

    def test_let_aopplus_to_code(self):
        """加算式x=y+zの中間表現をアセンブリに変換するテスト"""
        expected = [codegen.Instruction("lw", ("$t0", "-8($fp)")),
                    codegen.Instruction("lw", ("$t1", "-12($fp)")),
                    codegen.Instruction("add", ("$t0", "$t0", "$t1")),
                    codegen.Instruction("sw", ("$t0", "-4($fp)"))]

        x = sa.Decl("x", 2, "var", "int", -4)
        y = sa.Decl("y", 2, "var", "int", -8)
        z = sa.Decl("z", 2, "var", "int", -12)
        intermed_aop = ic.ArithmeticOperation("PLUS", y, z)
        intermed_let = ic.LetStatement(x, intermed_aop)
        actual = self.code_generator.intermed_stmt_to_code(12, 0, intermed_let)

        nose.tools.ok_(expected == actual)

    def test_let_aopminus_to_code(self):
        """減算式x=y+zの中間表現をアセンブリに変換するテスト"""
        expected = [codegen.Instruction("lw", ("$t0", "-8($fp)")),
                    codegen.Instruction("lw", ("$t1", "-12($fp)")),
                    codegen.Instruction("sub", ("$t0", "$t0", "$t1")),
                    codegen.Instruction("sw", ("$t0", "-4($fp)"))]

        x = sa.Decl("x", 2, "var", "int", -4)
        y = sa.Decl("y", 2, "var", "int", -8)
        z = sa.Decl("z", 2, "var", "int", -12)
        intermed_aop = ic.ArithmeticOperation("MINUS", y, z)
        intermed_let = ic.LetStatement(x, intermed_aop)
        actual = self.code_generator.intermed_stmt_to_code(12, 0, intermed_let)

        nose.tools.ok_(expected == actual)

    def test_let_aoptimes_to_code(self):
        """乗算式x=y+zの中間表現をアセンブリに変換するテスト"""
        expected = [codegen.Instruction("lw", ("$t0", "-8($fp)")),
                    codegen.Instruction("lw", ("$t1", "-12($fp)")),
                    codegen.Instruction("mul", ("$t0", "$t0", "$t1")),
                    codegen.Instruction("sw", ("$t0", "-4($fp)"))]

        x = sa.Decl("x", 2, "var", "int", -4)
        y = sa.Decl("y", 2, "var", "int", -8)
        z = sa.Decl("z", 2, "var", "int", -12)
        intermed_aop = ic.ArithmeticOperation("TIMES", y, z)
        intermed_let = ic.LetStatement(x, intermed_aop)
        actual = self.code_generator.intermed_stmt_to_code(12, 0, intermed_let)

        nose.tools.ok_(expected == actual)

    def test_let_aopdivide_to_code(self):
        """除算式x=y+zの中間表現をアセンブリに変換するテスト"""
        expected = [codegen.Instruction("lw", ("$t0", "-8($fp)")),
                    codegen.Instruction("lw", ("$t1", "-12($fp)")),
                    codegen.Instruction("div", ("$t0", "$t0", "$t1")),
                    codegen.Instruction("sw", ("$t0", "-4($fp)"))]

        x = sa.Decl("x", 2, "var", "int", -4)
        y = sa.Decl("y", 2, "var", "int", -8)
        z = sa.Decl("z", 2, "var", "int", -12)
        intermed_aop = ic.ArithmeticOperation("DIVIDE", y, z)
        intermed_let = ic.LetStatement(x, intermed_aop)
        actual = self.code_generator.intermed_stmt_to_code(12, 0, intermed_let)

        nose.tools.ok_(expected == actual)

    def test_let_relopeq_to_code(self):
        """条件式x = y == zの中間表現をアセンブリに変換するテスト"""
        expected = [codegen.Instruction("lw", ("$t0", "-8($fp)")),
                    codegen.Instruction("lw", ("$t1", "-12($fp)")),
                    codegen.Instruction("seq", ("$t0", "$t0", "$t1")),
                    codegen.Instruction("sw", ("$t0", "-4($fp)"))]

        x = sa.Decl("x", 2, "var", "int", -4)
        y = sa.Decl("y", 2, "var", "int", -8)
        z = sa.Decl("z", 2, "var", "int", -12)
        intermed_aop = ic.RelationalExpression("EQUAL", y, z)
        intermed_let = ic.LetStatement(x, intermed_aop)
        actual = self.code_generator.intermed_stmt_to_code(12, 0, intermed_let)

        nose.tools.ok_(expected == actual)

    def test_let_relopne_to_code(self):
        """条件式x = y != zの中間表現をアセンブリに変換するテスト"""
        expected = [codegen.Instruction("lw", ("$t0", "-8($fp)")),
                    codegen.Instruction("lw", ("$t1", "-12($fp)")),
                    codegen.Instruction("sne", ("$t0", "$t0", "$t1")),
                    codegen.Instruction("sw", ("$t0", "-4($fp)"))]

        x = sa.Decl("x", 2, "var", "int", -4)
        y = sa.Decl("y", 2, "var", "int", -8)
        z = sa.Decl("z", 2, "var", "int", -12)
        intermed_aop = ic.RelationalExpression("NEQ", y, z)
        intermed_let = ic.LetStatement(x, intermed_aop)
        actual = self.code_generator.intermed_stmt_to_code(12, 0, intermed_let)

        nose.tools.ok_(expected == actual)

    def test_let_relopgt_to_code(self):
        """条件式x = y > zの中間表現をアセンブリに変換するテスト"""
        expected = [codegen.Instruction("lw", ("$t0", "-8($fp)")),
                    codegen.Instruction("lw", ("$t1", "-12($fp)")),
                    codegen.Instruction("sgt", ("$t0", "$t0", "$t1")),
                    codegen.Instruction("sw", ("$t0", "-4($fp)"))]

        x = sa.Decl("x", 2, "var", "int", -4)
        y = sa.Decl("y", 2, "var", "int", -8)
        z = sa.Decl("z", 2, "var", "int", -12)
        intermed_aop = ic.RelationalExpression("GT", y, z)
        intermed_let = ic.LetStatement(x, intermed_aop)
        actual = self.code_generator.intermed_stmt_to_code(12, 0, intermed_let)

        nose.tools.ok_(expected == actual)

    def test_let_reloplt_to_code(self):
        """条件式x = y < zの中間表現をアセンブリに変換するテスト"""
        expected = [codegen.Instruction("lw", ("$t0", "-8($fp)")),
                    codegen.Instruction("lw", ("$t1", "-12($fp)")),
                    codegen.Instruction("slt", ("$t0", "$t0", "$t1")),
                    codegen.Instruction("sw", ("$t0", "-4($fp)"))]

        x = sa.Decl("x", 2, "var", "int", -4)
        y = sa.Decl("y", 2, "var", "int", -8)
        z = sa.Decl("z", 2, "var", "int", -12)
        intermed_aop = ic.RelationalExpression("LT", y, z)
        intermed_let = ic.LetStatement(x, intermed_aop)
        actual = self.code_generator.intermed_stmt_to_code(12, 0, intermed_let)

        nose.tools.ok_(expected == actual)

    def test_let_relopge_to_code(self):
        """条件式x = y == zの中間表現をアセンブリに変換するテスト"""
        expected = [codegen.Instruction("lw", ("$t0", "-8($fp)")),
                    codegen.Instruction("lw", ("$t1", "-12($fp)")),
                    codegen.Instruction("sge", ("$t0", "$t0", "$t1")),
                    codegen.Instruction("sw", ("$t0", "-4($fp)"))]

        x = sa.Decl("x", 2, "var", "int", -4)
        y = sa.Decl("y", 2, "var", "int", -8)
        z = sa.Decl("z", 2, "var", "int", -12)
        intermed_aop = ic.RelationalExpression("GEQ", y, z)
        intermed_let = ic.LetStatement(x, intermed_aop)
        actual = self.code_generator.intermed_stmt_to_code(12, 0, intermed_let)

        nose.tools.ok_(expected == actual)

    def test_let_relople_to_code(self):
        """条件式x = y == zの中間表現をアセンブリに変換するテスト"""
        expected = [codegen.Instruction("lw", ("$t0", "-8($fp)")),
                    codegen.Instruction("lw", ("$t1", "-12($fp)")),
                    codegen.Instruction("sle", ("$t0", "$t0", "$t1")),
                    codegen.Instruction("sw", ("$t0", "-4($fp)"))]

        x = sa.Decl("x", 2, "var", "int", -4)
        y = sa.Decl("y", 2, "var", "int", -8)
        z = sa.Decl("z", 2, "var", "int", -12)
        intermed_aop = ic.RelationalExpression("LEQ", y, z)
        intermed_let = ic.LetStatement(x, intermed_aop)
        actual = self.code_generator.intermed_stmt_to_code(12, 0, intermed_let)

        nose.tools.ok_(expected == actual)

    def test_writestmt_to_code(self):
        """メモリへの書き込み式*x=yの中間表現をアセンブリに変換するテスト"""
        expected = [codegen.Instruction("lw", ("$t0", "-24($fp)")),
                    codegen.Instruction("lw", ("$t1", "-4($fp)")),
                    codegen.Instruction("sw", ("$t0", "0($t1)"))]

        x = sa.Decl("x", 2, "var", ("pointer", "int"), -4)
        y = sa.Decl("y", 2, "var", "int", -24)
        intermed_write = ic.WriteStatement(x, y)
        actual = self.code_generator.intermed_stmt_to_code(24, 0, intermed_write)

        nose.tools.ok_(expected == actual)

    def test_readstmt_to_code(self):
        """メモリ参照式x=*yの中間表現をアセンブリに変換するテスト"""
        expected = [codegen.Instruction("lw", ("$t0", "-24($fp)")),
                    codegen.Instruction("lw", ("$t0", "0($t0)")),
                    codegen.Instruction("sw", ("$t0", "-4($fp)"))]

        x = sa.Decl("x", 2, "var", "int", -4)
        y = sa.Decl("y", 2, "var", ("pointer", "int"), -24)
        intermed_write = ic.ReadStatement(x, y)
        actual = self.code_generator.intermed_stmt_to_code(24, 0, intermed_write)

        nose.tools.ok_(expected == actual)

    def test_ifstmt_to_code(self):
        """if文 if(x) {y = x;} else {z = x;}の中間表現をアセンブリに変換するテスト"""
        label1 = self.code_generator.labelman.nextlabel()
        label2 = self.code_generator.labelman.nextlabel()
        expected = [codegen.Instruction("lw", ("$t0", "0($fp)")),
                    codegen.Instruction("beqz", ("$t0", label1)),
                    codegen.Instruction("lw", ("$t0", "0($fp)")),
                    codegen.Instruction("sw", ("$t0", "-4($fp)")),
                    codegen.Instruction("j", label2),
                    codegen.Label(label1),
                    codegen.Instruction("lw", ("$t0", "0($fp)")),
                    codegen.Instruction("sw", ("$t0", "-8($fp)")),
                    codegen.Label(label2)]

        self.code_generator.labelman.reset() # ラベル番号をリセット

        temp0 = sa.Decl("_t0", 2, "temp", "int", -12) # x(0($fp))評価結果 いるか…？
        x = sa.Decl("x", 2, "var", "int", 0)
        y = sa.Decl("y", 2, "var", "int", -4)
        z = sa.Decl("z", 2, "var", "int", -8)
        let_y = ic.LetStatement(y, ic.VarExpression(x))
        let_z = ic.LetStatement(z, ic.VarExpression(x))
        comp_then = ic.CompoundStatement([], [let_y])
        comp_else = ic.CompoundStatement([], [let_z])
        intermed_if = ic.IfStatement(x, comp_then, comp_else)
        actual = self.code_generator.intermed_stmt_to_code(12, 0, intermed_if)

        nose.tools.ok_(expected == actual)

    def test_whilestmt_to_code(self):
        """while(x) {print(x);}の中間表現をアセンブリに変換するテスト"""
        label1 = self.code_generator.labelman.nextlabel()
        label2 = self.code_generator.labelman.nextlabel()
        expected = [codegen.Instruction("lw", ("$t0", "-4($fp)")),
                    codegen.Instruction("beqz", ("$t0", label2)),
                    codegen.Label(label1),
                    codegen.Instruction("li", ("$v0", 1)),
                    codegen.Instruction("lw", ("$t0", "-4($fp)")),
                    codegen.Instruction("move", ("$a0", "$t0")),
                    codegen.Instruction("syscall", ()),
                    codegen.Instruction("li", ("$v0", 4)),
                    codegen.Instruction("la", ("$a0", "nl")),
                    codegen.Instruction("syscall", ()),
                    codegen.Instruction("lw", ("$t0", "-4($fp)")),
                    codegen.Instruction("beqz", ("$t0", label2)),
                    codegen.Instruction("j", label1),
                    codegen.Label(label2)]

        self.code_generator.labelman.reset()

        x = sa.Decl("x", 2, "var", "int", -4)
        intermed_print = ic.PrintStatement(x)
        comp = ic.CompoundStatement([], [intermed_print])
        intermed_while = ic.WhileStatement(x, comp)
        actual = self.code_generator.intermed_stmt_to_code(4, 0, intermed_while)

        nose.tools.ok_(expected == actual)

    def test_returnstmt_to_code(self):
        """return x;の中間表現をアセンブリに変換するテスト"""
        expected = flatten([codegen.Instruction("lw", ("$t0", "-4($fp)")),
                    codegen.Instruction("move", ("$v0", "$t0")),
                    self.code_generator.restore_frame(4, 0)])

        x = sa.Decl("x", 2, "var", "int", -4)
        intermed_return = ic.ReturnStatement(x)
        actual = self.code_generator.intermed_stmt_to_code(4, 0, intermed_return)

        nose.tools.ok_(expected == actual)

if __name__ == '__main__':
    nose.main(argv=['nose', '-v'])
