#!/usr/bin/python
# -*- coding: utf-8 -*-

import codegen

def convert_to_string(line):
    if isinstance(line, str):
        return line
    else:
        return str(line)


class PrintCode(object):

    def __init__(self, code):
        self.strcode = ""
        self.code = code

    def struct_to_string(self, struct):
        """アセンブリを表すクラスインスタンスを受け取り、文字列に変換する関数"""
        if isinstance(struct, codegen.Instruction):
            op = struct.op
            if isinstance(struct.args, tuple):
                args_str = ",".join(map(str, struct.args))
            else:
                args_str = str(struct.args)

            return "    " + op + " " + args_str + "\n"

        elif isinstance(struct, codegen.Label):
            return struct.name + ":\n"

        elif isinstance(struct, codegen.Directive):
            label = struct.label
            # args_str = ",".join(map(str, struct.args))
            if isinstance(struct.args, tuple):
                args_str = ",".join(map(str, struct.args))
            else:
                args_str = str(struct.args)

            return "    " + label + " " + args_str  + "\n"

    def code_to_string(self):
        """アセンブリコードを表すクラスインスタンスのリストを受け取り、
           それらを文字列に変換したものを返す関数"""
        for struct in self.code:
            self.strcode += self.struct_to_string(struct)

        return self.strcode