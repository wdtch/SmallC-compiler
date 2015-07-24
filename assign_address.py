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
            # グローバル宣言
            if isinstance(itmdelem, ic.VarDecl):
                if isinstance(itmdelem.var.objtype, tuple) and \
                    itmdelem.var.objtype[0] == "array":
                    self.intermed_code[i].var.offset = self.ofs_to_globalarray(itmdelem.var.objtype[2])
                else:
                    self.intermed_code[i].var.offset = self.ofs_to_globalvar()

            # 関数定義
            elif isinstance(itmdelem, ic.FunctionDefinition):
                self.ofsman.reset()
                # パラメータ
                for j, param in enumerate(itmdelem.params):
                    if isinstance(param.var.objtype, tuple) and \
                        param.var.objtype[0] == "array":
                        self.intermed_code[i].params[j].var.offset = self.ofs_to_arrayparam(param.var.objtype[2])
                    else:
                        self.intermed_code[i].params[j].var.offset = self.ofs_to_param()

                # self.ofsman.reset()

                # 関数内での宣言
                for k, decl in enumerate(itmdelem.body.decls):
                    if isinstance(decl.var.objtype, tuple) and \
                        decl.var.objtype[0] == "array":
                        self.intermed_code[i].body.decls[k].var.offset = self.ofs_to_arrayvar(decl.var.objtype[2])
                    else:
                        print("assining address to declaration in function...")
                        self.intermed_code[i].body.decls[k].var.offset = self.ofs_to_var()
                        print(self.intermed_code[i].body.decls[k].var.__dict__)

                # self.ofsman.reset()

                # 関数内の複文に含まれる宣言
                # for stmt in itmdelem.body.stmts:
                #     self.assign_address_to_stmt(stmt)
                self.assign_address_to_compstmt(itmdelem.body)

                itmdelem.localvarsize = -1 * (self.ofsman.current_varoffset - 4)
                itmdelem.paramsize = self.ofsman.current_paramoffset

                # self.ofsman.reset()

        return self.intermed_code

    def assign_address_to_compstmt(self, compstmt):
        """引数として取った複文の宣言と、文に含まれる一時変数の宣言にアドレスを割り当てる"""
        print("assining address to compound statement...")
        # 宣言
        for decl in compstmt.decls:
            if isinstance(decl.var.objtype, tuple) and \
                decl.var.objtype[0] == "array":
                if decl.var.offset == -1:
                    decl.var.offset = self.ofs_to_arrayvar(decl.var.objtype[2])
            else:
                print("found declaration.")
                if decl.var.offset == -1:
                    decl.var.offset = self.ofs_to_var()
                    print(decl.var.__dict__)

        # self.ofsman.reset()

        # 複文(を含む可能性のある中間表現)に含まれる複文に再帰的にアドレス割り当て
        for stmt in compstmt.stmts:
            if isinstance(stmt, ic.CompoundStatement):
                self.assign_address_to_compstmt(stmt)

            elif isinstance(stmt, ic.IfStatement):
                if isinstance(stmt.then_stmt, ic.CompoundStatement):
                    self.assign_address_to_compstmt(stmt.then_stmt)
                else:
                    # とりあえずprintだけ
                    # print(stmt.then_stmt)
                    # print(stmt.then_stmt.__dict__)
                    pass

                if isinstance(stmt.else_stmt, ic.CompoundStatement):
                    self.assign_address_to_compstmt(stmt.else_stmt)
                else:
                    # とりあえずprintだけ
                    # print(stmt.else_stmt)
                    # print(stmt.else_stmt.__dict__)
                    pass

            elif isinstance(stmt, ic.WhileStatement):
                if isinstance(stmt, ic.CompoundStatement):
                    self.assign_address_to_compstmt(stmt.stmt)
                else:
                    # print(stmt.stmt)
                    # print(stmt.stmt.__dict__)
                    pass

            elif isinstance(stmt, ic.LetStatement):
                if stmt.var.kind == "temp" and stmt.var.offset == -1:
                    stmt.var.offset = self.ofs_to_var()
                if isinstance(stmt.exp, ic.VarExpression) and stmt.exp.var.offset == -1:
                    stmt.exp.var.offset = self.ofs_to_var()

            elif isinstance(stmt, ic.CallStatement) and stmt.dest.offset == -1:
                stmt.dest.offset = self.ofs_to_var()

        return compstmt

    def ofs_to_var(self):
        """局所変数に割り当てるアドレスを計算し、その値を返す"""
        self.ofsman.next_ofs_var()
        offset_var = self.ofsman.current_varoffset

        return offset_var

    def ofs_to_param(self):
        """パラメータに割り当てるアドレスを計算し、その値を返す"""
        self.ofsman.next_ofs_param()
        offset_param = self.ofsman.current_paramoffset

        return offset_param

    def ofs_to_globalvar(self):
        """グローバル変数に割り当てるアドレスを計算し、その値を返す"""
        self.ofsman.next_ofs_var()
        offset_globalvar = self.ofsman.current_varoffset

        return offset_globalvar

    def ofs_to_arrayvar(self, size):
        """配列型の局所変数に割り当てるアドレスを計算し、その値を返す"""
        for _ in range(size):
            self.ofsman.next_ofs_var()
        offset_array = self.ofsman.current_varoffset

        return offset_array

    def ofs_to_arrayparam(self, size):
        """配列型のパラメータに割り当てるアドレスを計算し、その値を返す"""
        for _ in range(size):
            self.ofsman.next_ofs_param()
        offset_paramarray = self.ofsman.current_paramoffset

        return offset_paramarray

    def ofs_to_globalarray(self, size):
        """配列型のグローバル変数に割り当てるアドレスを計算し、その値を返す"""
        for _ in range(size):
            self.ofsman.next_ofs_var()
        offset_globalarray = self.ofsman.current_varoffset

        return offset_globalarray

    # def assign_ofs_to_compstmt(self, compstmt):
    #     """関数定義内の複文、またはその複文に含まれる複文(if, while文の中)から
    #        宣言を見つけてアドレスを割り当てる"""
    #     if isinstance(stmt, ic.IfStatement):
    #         for then_decl in stmt.then_stmt.decls:
    #             if isinstance(then_decl.var.objtype, tuple) and \
    #                 then_decl.var.objtype[0] == "array":
    #                 then_decl.var.offset = self.ofs_to_arrayvar()
    #             else:
    #                 then_decl.var.offset = self.ofs_to_var()

    #         for then_stmtelem in stmt.then_stmt.stmts:
    #             self.assign_address_to_stmt(then_stmtelem)

    #         for else_decl in stmt.else_stmt.decls:
    #             if isinstance(else_decl.var.objtype, tuple) and \
    #                 else_decl.var.objtype[0] == "array":
    #                 else_decl.var.offset = self.ofs_to_arrayvar()
    #             else:
    #                 else_decl.var.offset = self.ofs_to_var()

    #         for else_stmtelem in stmt.else_stmt.stmts:
    #             self.assign_address_to_stmt(self, else_stmtelem)

    #     elif isinstance(stmt, ic.WhileStatement):
    #         for while_decl in stmt.stmt.decls:
    #             if isinstance(while_decl.var.objtype, tuple) and \
    #                 while_decl.var.objtype[0] == "array":
    #                 while_decl.var.offset = self.ofs_to_arrayvar()
    #             else:
    #                 while_decl.var.offset = self.ofs_to_var()

    #         for while_stmt in stmt.stmt.stmts:
    #             self.assign_address_to_stmt(while_stmt)

    #     for decl in compstmt.decls:
    #         if isinstance(decl.var.objtype, tuple) and \
    #             decl.var.objtype[0] == "array":
    #             decl.var.offset = self.ofs_to_arrayvar()
    #         else:
    #             decl.var.offset = self.ofs_to_var()

    #     for stmt in compstmt.stmts:
    #         if


class OffsetManager(object):

    def __init__(self, wordsize):
        self.init_varoffset = 4
        self.init_paramoffset = 0
        self.current_varoffset = self.init_varoffset
        self.current_paramoffset = self.init_paramoffset
        self.wordsize = wordsize

    def next_ofs_var(self):
        """局所変数に割り当てるオフセットをwordsizeの分だけ下にずらす"""
        self.current_varoffset = self.current_varoffset - self.wordsize

    def next_ofs_param(self):
        """パラメータに割り当てるオフセットをwordsizeの分だけ上にずらす"""
        self.current_paramoffset = self.current_paramoffset + self.wordsize

    def reset(self):
        self.current_varoffset = self.init_varoffset
        self.current_paramoffset = self.init_paramoffset