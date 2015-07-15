#!/usr/bin/python
# -*- coding: utf-8 -*-

import semantic_analyzer as sa
import intermed_code as ic


class AssignAddress(object):

    def __init__(self, intermed_code):
        self.intermed_code = intermed_code
        self.wordsize = 4
        self.ofsman = OffsetManager(self.wordsize)

    def assign_address(self):
        """self.intermed_codeに保存されている中間表現列を辿り、
           宣言を見つけ出して種類に応じたアドレス割り当て関数に送る
           全ての宣言にアドレスを割り当てた後、書き換えた中間表現を返す"""
        for i, itmdelem in enumerate(self.intermed_code):
            if isinstance(itmdelem, ic.VarDecl):
                if isinstance(itmdelem.var.objtype, tuple) and \
                    itmdelem.var.objtype[0] == "array":
                    self.intermed_code[i].var.offset = self.ofs_to_globalarray()
                else:
                    self.intermed_code[i].var.offset = self.ofs_to_globalvar()

            elif isinstance(itmdelem, ic.FunctionDefinition):
                self.ofsman.reset()

                for j, param in enumerate(itmdelem.params):
                    if isinstance(param.var.objtype, tuple) and \
                        param.var.objtype[0] == "array":
                        self.intermed_code[i].params[j].var.offset = self.ofs_to_arrayparam()
                    else:
                        self.intermed_code[i].params[j].var.offset = self.ofs_to_param()

                self.ofsman.reset()

                for k, decl in enumerate(itmdelem.body.decls):
                    if isinstance(itmdelem.var.objtype, tuple) and \
                        itmdelem.var.objtype[0] == "array":
                        self.intermed_code[i].body.decls[k].var.offset = self.ofs_to_arrayvar()
                    else:
                        self.intermed_code[i].body.decls[k].var.offset = self.ofs_to_var()

                self.ofsman.reset()

        return self.intermed_code

    def ofs_to_var(self):
        """局所変数に割り当てるアドレスを計算し、その値を返す"""
        self.ofsman.next_ofs_var()
        offset_var = self.ofsman.current_offset
        return offset_var

    def ofs_to_param(self):
        """パラメータに割り当てるアドレスを計算し、その値を返す"""
        self.ofsman.next_ofs_param()
        offset_param = self.ofsman.current_offset
        return offset_param

    def ofs_to_globalvar(self):
        """グローバル変数に割り当てるアドレスを計算し、その値を返す"""
        self.ofsman.next_ofs_var()
        offset_globalvar = self.ofsman.current_offset
        return offset_globalvar

    def ofs_to_arrayvar(self, size):
        """配列型の局所変数に割り当てるアドレスを計算し、その値を返す"""
        for _ in range(size):
            self.ofsman.next_ofs_var()
        offset_array = self.ofsman.current_offset

        return offset_array

    def ofs_to_arrayparam(self, size):
        """配列型のパラメータに割り当てるアドレスを計算し、その値を返す"""
        for _ in range(size):
            self.ofsman.next_ofs_param()
        offset_paramarray = self.ofsman.current_offset

        return offset_paramarray

    def ofs_to_globalarray(self, size):
        """配列型のグローバル変数に割り当てるアドレスを計算し、その値を返す"""
        for _ in range(size):
            self.ofsman.next_ofs_var()
        offset_globalarray = self.ofsman.current_offset

        return offset_globalarray

class OffsetManager(object):

    def __init__(self, wordsize):
        self.init_offset = 0
        self.current_offset = self.init_offset
        self.wordsize = wordsize

    def next_ofs_var(self):
        """局所変数に割り当てるオフセットをwordsizeの分だけ下にずらす"""
        self.current_offset = self.current_offset - self.wordsize

    def next_ofs_param(self):
        """パラメータに割り当てるオフセットをwordsizeの分だけ上にずらす"""
        self.current_offset = self.current_offset + self.wordsize

    def reset(self):
        self.current_offset = self.init_offset