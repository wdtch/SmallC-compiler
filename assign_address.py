#!/usr/bin/python
# -*- coding: utf-8 -*-

import intermed_code as ic


class AssignAddress(object):

    def __init__(self, intermed_code):
        self.intermed_code = intermed_code
        self.ofsman = OffsetManager()
        self.wordsize = 4

    def assign_address(self):
        """self.intermed_codeに保存されている中間表現列を辿り、
           宣言を見つけ出して種類に応じたアドレス割り当て関数に送る
           全ての宣言にアドレスを割り当てた後、書き換えた中間表現を返す"""
        for itmdelem in intermed_code:
            if isinstance(itmdelem)
        return self.intermed_code

    def ofs_to_var(self):
        """局所変数に割り当てるアドレスを計算し、その値を返す"""

        return offset_var

    def ofs_to_param(self):
        """パラメータに割り当てるアドレスを計算し、その値を返す"""

        return offset_param

    def ofs_to_globalvar(self):
        """グローバル変数に割り当てるアドレスを計算し、その値を返す"""

        return offset_globalvar

    def ofs_to_arrayvar(self):
        """配列型の局所変数に割り当てるアドレスを計算し、その値を返す"""

        return offset_array

    def ofs_to_arrayparam(self):
        """配列型のパラメータに割り当てるアドレスを計算し、その値を返す"""

        return offset_paramarray

    def ofs_to_globalarray(self):
        """配列型のグローバル変数に割り当てるアドレスを計算し、その値を返す"""

        return offset_globalarray

class OffsetManager(object):

    def __init__(self):
        self.init_offset = 0
        self.current_offset = self.init_offset

    def next_ofs_var(self):
        """局所変数に割り当てるオフセットをwordsizeの分だけ下にずらす"""

    def next_ofs_param(self):
        """パラメータに割り当てるオフセットをwordsizeの分だけ上にずらす"""