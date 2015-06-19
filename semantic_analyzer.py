#!/usr/bin/python
# -*- coding: utf-8 -*-

"""意味解析モジュール"""

from __future__ import unicode_literals
import sys
import ast

class Decl(object):
    def __init__(self, name, level, kind, objtype):
        self.name = name
        self.level = level
        self.kind = kind
        self.objtype = objtype

class Environment(Decl):
    def __init__(self, decl=None):
        if decl is None:
            self.decl_list = []
        else:
            self.decl_list = [decl]

    def add(self, decl):
        self.decl_list.append(decl)

    # if the object which has the same name is found, return the Decl class object, otherwise return None
    def lookup(self, name):
        for decl in self.decl_list:
            if name == decl.name:
                return decl

class Analyzer(object):
    def __init__(self, ast_top):
        self.nodelist = ast_top
        self.env = Environment()


    def analyze_declaration(self, declaration_node, declarator, level): # for ast.Declaration
        print("Begin analyzing declaration.")
        # 抽象構文木をたどって変数名を取ってくる
        name = declarator.direct_declarator.identifier.identifier
        print("{0}".format(name))
        if declarator.kind == "NORMAL":
            if isinstance(declarator.direct_declarator, ast.DirectDeclarator):
                objtype = "int"
            elif isinstance(declarator.direct_declarator, ast.DirectArrayDeclarator):
                objtype = ("array", "int", declarator.direct_declarator.constant.value)
        elif declarator.kind == "POINTER":
            if isinstance(declarator.direct_declarator, ast.DirectDeclarator):
                objtype = ("pointer", "int")
            elif isinstance(declarator.direct_declarator, ast.DirectArrayDeclarator):
                objtype = ("pointer", "array")

        decl_decl = Decl(name, level, "var", objtype)

        # for debug
        print("new Decl class object of declaration: {0}".format(decl_decl))
        print("name: {0}".format(decl_decl.name))
        print("level: {0}".format(decl_decl.level))
        print("kind: {0}".format(decl_decl.kind))
        print("type: {0}".format(decl_decl.objtype))

        return decl_decl


    def analyze_statement(self, statement_node, level):
        pass

    def analyze_func_prototype(self, proto_node, level):
        if level != 0:
            sys.stderr.write("Prototype function declaration is available only at top-level.")
        else:
            print("Begin analyzing function prototype.")
            # 抽象構文木をたどって関数名を取ってくる
            name = proto_node.function_declarator.identifier.identifier
            print("func-prototype name:{0}".format(name))

            kind = "proto"
            return_type = proto_node.type_specifier.type_specifier

            objtype = ["proto", return_type]
            if not isinstance(proto_node.function_declarator.parameter_type_list, ast.NullNode):
                for param in proto_node.function_declarator.parameter_type_list.nodes:
                    if param.parameter_declarator.kind == "NORMAL":
                        objtype.append(param.type_specifier.type_specifier)
                    elif param.parameter_declarator.kind == "POINTER":
                        objtype.append(("pointer", param.type_specifier.type_specifier))

        decl_proto = Decl(name, level, kind, tuple(objtype))

        # for debug
        print("new Decl class object of prototype: {0}".format(decl_proto))
        print("name: {0}".format(decl_proto.name))
        print("level: {0}".format(decl_proto.level))
        print("kind: {0}".format(decl_proto.kind))
        print("type: {0}".format(decl_proto.objtype))

        return decl_proto


    def analyze_func_definition(self, funcdef_node, level):
        pass


    def analyze(self, nodelist, level=0):
        if isinstance(nodelist, ast.ExternalDeclarationList):
            print("Analyze nodes in external declaration list.")
            for node in nodelist.nodes:
                self.analyze(node, level)

        elif isinstance(nodelist, ast.Declaration):
            for declarator in nodelist.declarator_list.nodes:
                decl_decl = self.analyze_declaration(nodelist, declarator, level)
                if self.env.lookup(decl_decl.name) == None:
                    print("OK: No duplication in environment.")
                    self.env.add(decl_decl)
                else:
                    existing_decl = self.env.lookup(decl_decl.name)
                    if existing_decl.kind == "fun" or existing_decl.kind == "proto":
                        if existing_decl.level == 0:
                            sys.stderr.write("Error: {0} is defined as a function.".format(decl_decl.name))
                        else:
                            self.env.add(decl_decl)
                    elif existing_decl.kind == "var":
                        if existing_decl.level == decl_decl.level:
                            sys.stderr.write("Error: Duplicate declaration - {0}".format(decl_decl.name))
                    elif existing_decl.kind == "param":
                        self.env.add(decl_decl)
                        print("Warning: This variable declaration is duplicated - param {0}".format(existing_decl.name))

        elif isinstance(nodelist, ast.FunctionPrototype):
            decl_proto = self.analyze_func_prototype(nodelist, level)
            if self.env.lookup(decl_proto.name) == None:
                    print("OK: No duplication in environment.")
                    self.env.add(decl_proto)
            else:
                existing_decl = self.env.lookup(decl_proto.name)
                if existing_decl.kind == "fun":
                    if existing_decl.type != decl_proto.type:
                        sys.stderr.write("Error: Conflicting {0} prototype definition with {1} function.".format(decl_proto.type, existing_decl.type))
                    else:
                        self.env.add(decl_proto)
                elif existing_decl.kind == "proto":
                    if existing_decl.proto == decl_proto.type:
                        sys.stderr.write("Error: Type inconsintency of duplicate prototype definition - {0}".format(decl_proto.name))
                    else:
                        self.env.add(decl_proto)
                elif existing_decl.kind == "var":
                    if existing_decl.level == 0:
                        sys.stderr.write("Error: Duplicate prototype declaration with global variable: {0}".format(decl_proto.name))
                    else:
                        self.env.add(decl_proto)

        return self.env
