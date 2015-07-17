#!/usr/bin/python
# -*- coding: utf-8 -*-

import semantic_analyzer
import intermed_code as ic
import collections

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


class Instruction(object):

    """命令を表すクラス。opはMIPSアセンブリの命令に対応する文字列であり、argsは命令を
       実行する際の引数のリストである。"""

    def __init__(self, op, args):
        self.op = op
        self.args = args

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Label(object):

    """ラベル(main:, L0:など)を表すクラス。nameはラベル名を表す。"""

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Directive(object):

    """ディレクティブ(.textなど)を表すクラス"""

    def __init__(self, label, args):
        self.label = label
        self.args = args

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Comment(object):

    """デバッグの際生成するコードにつけるコメントを表すクラス"""

    def __init__(self, arg):
        self.arg = arg

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class CodeGenerator(object):

    """MIPSのアセンブリコード生成のための変数と関数をまとめたクラス"""

    def __init__(self, intermed_code):
        self.intermed_code = intermed_code
        self.reg0 = "$t0"
        self.reg1 = "$t1"
        self.reg2 = "$t2"
        self.return_reg = "$v0"
        self.fpreg = "$fp"
        self.spreg = "$sp"
        self.labelman = LabelManager()
        self.wordsize = 4

    def allocate_frame(self, localvarsize, paramsize):
        """関数呼び出しの先頭で実行される。局所変数のワードサイズlocalvarsizeと
           パラメータのワードサイズparamsizeからその関数のために確保する
           関数フレームのサイズを計算し、それを確保する命令列を返す"""
        local_fp_ra_size = localvarsize + 2 * self.wordsize
        framesize = local_fp_ra_size + paramsize
        allocate_instrs = [Instruction("subu", (self.spreg, self.spreg, framesize)),
                           Instruction("sw", ("$ra", "4($sp)")),
                           Instruction("sw", ("$fp", "0($sp)")),
                           Instruction("addiu", (self.fpreg, self.spreg, (local_fp_ra_size - 4)))]

        return allocate_instrs

    def restore_frame(self, localvarsize, paramsize):
        """関数呼び出しの末尾で実行される。$fpと$raの値を関数呼び出し前の値に戻し、
           関数フレームも元に戻して$raに記録されている場所にジャンプする命令列を返す"""
        local_fp_ra_size = localvarsize + 2 * self.wordsize
        framesize = local_fp_ra_size + paramsize
        restore_instrs = [Instruction("lw", (self.fpreg, "0($sp)")),
                          Instruction("lw", ("$ra", "4($sp)")),
                          Instruction(
                              "addiu", (self.spreg, self.spreg, framesize)),
                          Instruction("jr", "$ra")]

        return restore_instrs

    def varofs_to_fp(self, vardecl):
        """局所変数またはパラメータから作られたDecl型のオブジェクトを受け取って、そこから読み取った
           オフセットの値を元に$fp経由でアクセスするためのアドレス式を返す"""
        offset = vardecl.offset
        return str(offset) + "($fp)"

    def argofs_to_sp(self, paramdecl):
        """引数を表すDecl型のオブジェクトを受け取って、そこから読み取った
           オフセットの値を元に$sp経由でアクセスするためのアドレス式を返す"""
        offset = paramdecl.offset
        return str(offset) + "($sp)"

    def intermed_exp_to_code(self, dest, exp):
        """VarExpression型の値destと中間命令式expを受け取って、eを評価しdestに結果を書き込む
           アセンブリ命令列を返す"""
        instr_list = []

        if isinstance(exp, ic.IntExpression):
            value = exp.num
            destaddr = self.varofs_to_fp(dest)
            instr_list = [Instruction("li", (self.reg0, value)),
                          Instruction("sw", (self.reg0, destaddr))]

        elif isinstance(exp, ic.VarExpression):
            arg = exp.var
            argaddr = self.varofs_to_fp(arg)
            destaddr = self.varofs_to_fp(dest.var)
            instr_list = [Instruction("lw", (self.reg0, argaddr)),
                          Instruction("sw", (self.reg0, destaddr))]

        elif isinstance(exp, ic.ArithmeticOperation):
            if exp.op == "PLUS":
                op = "add"
            elif exp.op == "MINUS":
                op = "sub"
            elif exp.op == "TIMES":
                op = "mul"
            elif exp.op == "DIVIDE":
                op = "div"
            elif exp.op = "AND":
                op = "and"
            elif exp.op = "OR":
                op = "or"

            if exp.var_left.objtype == exp.var_right.objtype == "int":
                addr_left = self.varofs_to_fp(exp.var_left)
                addr_right = self.varofs_to_fp(exp.var_right)
                destaddr = self.varofs_to_fp(dest.var)

                instr_list = [Instruction("lw", (self.reg0, addr_left)),
                              Instruction("lw", (self.reg1, addr_right)),
                              Instruction(op, (self.reg0, self.reg0, self.reg1)),
                              Instruction("sw", (self.reg0, destaddr))]

            # 配列の要素に…アクセスするっ…！
            elif exp.var_left == ("pointer", "int") or exp.var_right == ("pointer", "int"):
                pass # 保留

        elif isinstance(exp, ic.RelationalExpression):
            if exp.op == "LEQ":
                op = "sle"
            elif exp.op == "GEQ":
                op = "sge"
            elif exp.op == "LT":
                op = "slt"
            elif exp.op == "GT":
                op = "sgt"
            elif exp.op == "EQUAL":
                op = "seq"
            elif exp.op == "NEQ":
                op = "sne"

            addr_left = self.varofs_to_fp(exp.var_left)
            addr_right = self.varofs_to_fp(exp.var_right)
            destaddr = self.varofs_to_fp(dest.var)

            instr_list = [Instruction("lw", (self.reg0, addr_left)),
                          Instruction("lw", (self.reg1, addr_right)),
                          Instruction(op, (self.reg0, self.reg0, self.reg1)),
                          Instruction("sw", (self.reg0, destaddr))]

        return instr_list

    def intermed_stmt_to_code(self, localvarsize, paramsize, stmt):
        """中間命令文と、return文を変換するための局所変数サイズとパラメータサイズを
           受け取り、アセンブリに変換して返す"""
        instr_list = []

        if isinstance(stmt, ic.EmptyStatement):
            instr_list = [Instruction("nop", ())]

        elif isinstance(stmt, ic.WriteStatement):
            destaddr = self.varofs_to_fp(stmt.dest)
            srcaddr = self.varofs_to_fp(stmt.src)
            destderef = "0(" + str(self.reg1) + ")"
            instr_list = [Instruction("lw", (self.reg0, srcaddr)),
                          Instruction("lw", (self.reg1, destaddr)),
                          Instruction("sw", (self.reg0, destderef))]

        elif isinstance(stmt, ic.ReadStatement):
            destaddr = self.varofs_to_fp(stmt.dest)
            srcaddr = self.varofs_to_fp(stmt.src)
            reg0deref = "0(" + self.reg0 + ")"
            instr_list = [Instruction("lw", (self.reg0, srcaddr)),
                          Instruction("lw", (self.reg0, reg0deref)),
                          Instruction("sw", (self.reg0, destaddr))]

        elif isinstance(stmt, ic.LetStatement):
            dest = stmt.var
            exp = stmt.exp
            instr_list = self.intermed_exp_to_code(dest, exp)

        elif isinstance(stmt, ic.IfStatement):
            expaddr = self.intermed_exp_to_code(stmt.var)
            then_code = flatten([self.intermed_stmt_to_code(tstmt) for tstmt in stmt.then_stmt])
            else_code = flatten([self.intermed_stmt_to_code(estmt) for estmt in stmt.else_stmt])

            label1 = self.labelman.nextlabel()
            label2 = self.labelman.nextlabel()

            instr_list = flatten([Instruction("lw", (self.reg0, expaddr)),
                                  Instruction("beqz", (self.reg0, label1)),
                                  then_code,
                                  Instruction("j", label2),
                                  Label(label1),
                                  else_code,
                                  Label(label2)])

        elif isinstance(stmt, ic.WhileStatement):
            expaddr = self.varofs_to_fp(stmt.var)
            code_true = flatten([self.intermed_stmt_to_code(tstmt) for tstmt in stmt.stmt])
            loop_label = self.labelman.nextlabel()
            break_label = self.labelman.nextlabel()

            instr_list = flatten([Instruction("lw", (self.reg0, expaddr)),
                                  Instruction("beqz", (self.reg0, break_label)),
                                  Label(loop_label),
                                  code_true,
                                  Instruction("lw", (self.reg0, expaddr)),
                                  Instruction("beqz", (self.reg0, break_label)),
                                  Label(break_label)])

        elif isinstance(stmt, ic.ReturnStatement):
            retaddr = self.varofs_to_fp(stmt.var)
            instr_list = flatten([Instruction("lw", (self.reg0, retaddr)),
                                  Instruction("move", (self.return_reg, self.reg0)),
                                  self.restore_frame(localvarsize, paramsize)])

        elif isinstance(stmt, ic.CallStatement):
            destaddr = self.varofs_to_fp(stmt.dest)
            func = stmt.function
            args_control = []

            for i, argvar in enumerate(stmt.variables):
                args_control.append(Instruction("lw", (self.reg0, self.varofs_to_fp(argvar))))
                args_control.append(Instruction("sw", (self.reg0, str(-4 * (len(stmt.variables) - i)) + "($sp)")))

            instr_list = flatten([args_control,
                                  Instruction("jal", func),
                                  Instruction("sw", (self.return_reg, destaddr))])

        elif isinstance(stmt, ic.PrintStatement):
            varaddr = self.varofs_to_fp(stmt.var)
            instr_list = [Instruction("li", (self.return_reg, 1)),
                          Instruction("lw", (self.reg0, varaddr)),
                          Instruction("move", ("$a0", self.reg0)),
                          Instruction("syscall", ())]

        return instr_list

    def intermed_globalvar_to_code(self, vardecl):
        """グローバル変数から作られたVardecl型のオブジェクトを受け取って、そこから
           読み取ったオフセットの値を元に$gp経由でアクセスするためのアドレスを返す"""
        pass

    def intermed_fundef_to_code(self, fundef):
        """関数定義の中間命令を受け取って、その中の宣言と複文、関数定義本体をアセンブリに
           変換した結果を返す"""
        funcvar = fundef.var
        localvarsize = 4 * len(fundef.body.decls)
        paramsize = 4 * len(fundef.params)
        code = [self.intermed_stmt_to_code(localvarsize, paramsize, stmt) for stmt in fundef.body.stmts]

        instr_list = flatten([Label(funcvar.name),
                      self.allocate_frame(localvarsize, paramsize),
                      code,
                      self.restore_frame(localvarsize, paramsize)])

        print("------ intermed fundef to code ------")
        print(localvarsize)
        print(paramsize)
        print(code)
        print(instr_list)

        return instr_list

    def intermed_code_to_code(self):
        localvarsize = 0
        fundef = []

        print("------ intermed code to assembly ------")
        for itmd in self.intermed_code:
            print(itmd)
            if isinstance(itmd, ic.VarDecl):
                localvarsize += 4
            elif isinstance(itmd, ic.FunctionDefinition):
                localvarsize += 4 * len(itmd.body.decls)
                fundef.append(self.intermed_fundef_to_code(itmd))

        print("fundef: {0}".format(fundef))

        instr_list = flatten([Directive(".text", ()),
                              Directive(".globl", ("main")),
                              # グローバル変数の変換,
                              fundef])

        return instr_list



class LabelManager(object):

    """関数呼び出しの際に必要なラベルの名前を管理するクラス"""

    def __init__(self):
        self.labelnum = 0

    def nextlabel(self):
        label_name = "L" + str(self.labelnum)
        self.labelnum += 1

        return label_name

    def reset(self):
        self.labelnum = 0
