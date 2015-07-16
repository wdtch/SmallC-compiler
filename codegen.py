#!/usr/bin/python
# -*- coding: utf-8 -*-

import semantic_analyzer
import intermed_code

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
        self.return_reg = "$v0"
        self.fpreg = "$fp"
        self.labelman = LabelManager()

    def allocate_frame(self, localvarsize, paramsize):
        """関数呼び出しの先頭で実行される。局所変数のワードサイズlocalvarsizeと
           パラメータのワードサイズparamsizeからその関数のために確保する
           関数フレームのサイズを計算し、それを確保する命令列を返す"""
           pass

    def restore_frame(self, localvarsize, paramsize):
        """関数呼び出しの末尾で実行される。$fpと$raの値を関数呼び出し前の値に戻し、
           関数フレームも元に戻して$raに記録されている場所にジャンプする命令列を返す"""
           pass

    def varofs_to_fp(self, vardecl):
        """局所変数またはパラメータから作られたVarDecl型のオブジェクトを受け取って、そこから読み取った
           オフセットの値を元に$fp経由でアクセスするためのアドレス式を返す"""
           pass

    def argofs_to_sp(self, paramdecl):
        """引数を表すVarDecl型のオブジェクトを受け取って、そこから読み取った
           オフセットの値を元に$sp経由でアクセスするためのアドレス式を返す"""
           pass

    def intermed_exp_to_code(self, dest, exp):
        """VarDecl型の値destと中間命令式expを受け取って、eを評価しdestに結果を書き込む
           アセンブリ命令列を返す"""
           pass

    def intermed_stmt_to_code(self, localvarsize, paramsize, stmt):
        """中間命令文と、return文を変換するための局所変数サイズとパラメータサイズを
           受け取り、アセンブリに変換して返す"""
           pass

    def intermed_globalvar_to_code(self, vardecl):
        """グローバル変数から作られたVardecl型のオブジェクトを受け取って、そこから
           読み取ったオフセットの値を元に$gp経由でアクセスするためのアドレスを返す"""
           pass

    def intermed_fundef_to_code(self, fundef):
        """関数定義の中間命令を受け取って、その中の宣言と複文、関数定義本体をアセンブリに
           変換した結果を返す"""
           pass


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