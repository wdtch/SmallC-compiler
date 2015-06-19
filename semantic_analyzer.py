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
        for decl in decl_list:
            if name == decl.name:
                return decl


def analyze_declaration(declaration_node, declarator, level): # for ast.Declaration
    name = declarator.direct_declarator.identifier.identifier
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


def analyze_statement(statement_node, level):


def analyze_func_prototype(prototype_node, level):


def analyze_func_definition(funcdef_node, level):



def analyze(nodelist, level=0):
    env = Environment()

    if isinstance(nodelist, ast.ExternalDeclarationList):
        for node in nodelist.nodes:
            analyze(node, level)

    elif isinstance(nodelist, ast.Declaration):
        for declarator in nodelist.daclarator_list:
            decl_decl = analyze_declaration(nodelist, declarator, level)
            if env.lookup(decl_decl.name) == None:
                env.add(decl_decl)
            else:
                existing_decl = env.lookup(decl_decl.name)
                if existing_decl.kind == "fun" or existing_decl.kind == "proto":
                    if existing_decl.level == 0:
                        sys.stderr.write("{0} is defined as a function.".format(decl_decl.name))
                    else:
                        env.add(decl_decl)

                elif existing_decl.kind == "var":
                    if existing_decl.level == decl_decl.level:
                        sys.stderr.write("Duplicate declaration: {0}".format(decl_decl.name))
                elif existing_decl.kind == "param":
                    env.add(decl_decl)
                    print("This declaration is duplicated: param {0}".format(existing_decl.name))


