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


    # generate Decl object
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
            # if self.env.lookup(name) == None:
                # sys.stderr.write("Error - No instance referenced by pointer {0}.\n".format(name))
            # else:
                # referenced = self.env.lookup(name)
                # if referenced.kind == "var" or referenced.kind == "param":
                    # declarator.direct_declarator.identifier.identifier = referenced
                # elif referenced.kind == "fun":
                    # sys.stderr.write("Error - Pointer for variable {0} references function.\n".format(name))

            if isinstance(declarator.direct_declarator, ast.DirectDeclarator):
                objtype = ("pointer", "int")
            elif isinstance(declarator.direct_declarator, ast.DirectArrayDeclarator):
                objtype = ("pointer", "array")

        decl_decl = Decl(name, level, "var", objtype)
        # これでいいのか？
        declarator.direct_declarator.identifier.identifier = decl_decl

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
        if level != 0:
            sys.stderr.write("Function definition is available only at top-level.")
        else:
            print("Begin analyzing function definition.")
            # 抽象構文木をたどって関数名を取ってくる
            name = funcdef_node.function_declarator.identifier.identifier
            print("function definition name:{0}".format(name))

            kind = "fun"
            return_type = funcdef_node.type_specifier.type_specifier

            objtype = ["fun", return_type]
            if not isinstance(funcdef_node.function_declarator.parameter_type_list, ast.NullNode):
                for param in funcdef_node.function_declarator.parameter_type_list.nodes:
                    if param.parameter_declarator.kind == "NORMAL":
                        objtype.append(param.type_specifier.type_specifier)
                    elif param.parameter_declarator.kind == "POINTER":
                        objtype.append(("pointer", param.type_specifier.type_specifier))

        decl_funcdef = Decl(name, level, kind, tuple(objtype))

        # for debug
        print("new Decl class object of function definition: {0}".format(decl_funcdef))
        print("name: {0}".format(decl_funcdef.name))
        print("level: {0}".format(decl_funcdef.level))
        print("kind: {0}".format(decl_funcdef.kind))
        print("type: {0}".format(decl_funcdef.objtype))

        return decl_funcdef


    def analyze_param_declaration(self, paramdec_node, level):
        print("Begin analyzing parameter declaration.")
        # 抽象構文木をたどって変パラメータ宣言を取ってくる
        name = paramdec_node.parameter_declarator.identifier.identifier
        print("{0}".format(name))
        if paramdec_node.parameter_declarator.kind == "NORMAL":
            objtype = "int"
        elif paramdec_node.parameter_declarator.kind == "POINTER":
            objtype = ("pointer", "int")

        decl_param = Decl(name, level, "param", objtype)

        # for debug
        print("new Decl class object of parameter declaration: {0}".format(decl_param))
        print("name: {0}".format(decl_param.name))
        print("level: {0}".format(decl_param.level))
        print("kind: {0}".format(decl_param.kind))
        print("type: {0}".format(decl_param.objtype))

        return decl_param


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
                            sys.stderr.write("Error: {0} is defined as a function.\n".format(decl_decl.name))
                        else:
                            self.env.add(decl_decl)
                    elif existing_decl.kind == "var":
                        if existing_decl.level == decl_decl.level:
                            sys.stderr.write("Error: Duplicate declaration - {0}\n".format(decl_decl.name))
                    elif existing_decl.kind == "param":
                        self.env.add(decl_decl)
                        print("Warning: This variable declaration is duplicated - param {0}".format(existing_decl.name))
                print("")

        elif isinstance(nodelist, ast.FunctionPrototype):
            decl_proto = self.analyze_func_prototype(nodelist, level)
            if self.env.lookup(decl_proto.name) == None:
                    print("OK: No duplication in environment.")
                    self.env.add(decl_proto)
            else:
                existing_decl = self.env.lookup(decl_proto.name)
                if existing_decl.kind == "fun":
                    if existing_decl.objtype != decl_proto.objtype:
                        sys.stderr.write("Error: Conflicting {0} prototype definition with {1} function.\n".format(decl_proto.type, existing_decl.type))
                    else:
                        print("OK: Prototype declaration after function definition, type consisntent")
                        self.env.add(decl_proto)
                elif existing_decl.kind == "proto":
                    if existing_decl.objtype[1] != decl_proto.objtype[1]:
                        sys.stderr.write("Error: Type inconsintency of duplicate prototype definition - {0}\n".format(decl_proto.name))
                    else:
                        print("OK: Duplicate prototype declaration, but type consistent")
                        self.env.add(decl_proto)
                elif existing_decl.kind == "var":
                    if existing_decl.level == 0:
                        sys.stderr.write("Error: Duplicate prototype declaration with global variable: {0}\n".format(decl_proto.name))
                    else:
                        print("OK: Duplicate prototype declaration and variable declaration, but they are at different level.")
                        self.env.add(decl_proto)
            print("")
            self.analyze(nodelist.function_declarator.parameter_type_list, level+1)

        elif isinstance(nodelist, ast.FunctionDefinition):
            decl_funcdef = self.analyze_func_definition(nodelist, level)
            if self.env.lookup(decl_funcdef.name) == None:
                    print("OK: No duplication in environment.")
                    self.env.add(decl_funcdef)
            else:
                existing_decl = self.env.lookup(decl_funcdef.name)
                if existing_decl.kind == "fun":
                    sys.stderr.write("Error: Duplicate function definition - {0}.\n".format(decl_funcdef.name))
                elif existing_decl.kind == "proto":
                    if existing_decl.objtype != decl_funcdef.objtype:
                        sys.stderr.write("Error: Type inconsintency of function prototype and function definition - {0}\n".format(decl_funcdef.name))
                    else:
                        print("OK: Types of prototype and function definition are consistent")
                        self.env.add(decl_funcdef)
                elif existing_decl.kind == "var":
                    if existing_decl.level == 0:
                        sys.stderr.write("Error: Duplicate function definition with global variable - {0}\n".format(decl_funcdef.name))
                    else:
                        print("OK: Duplicate function definition and variable declaration, but they are at different level.")
                        self.env.add(decl_funcdef)
            print("")
            print("Begin analyzing parameter in function definition.")
            self.analyze(nodelist.function_declarator.parameter_type_list, level+1)
            print("Begin analyzing compound statement in function definition.")
            self.analyze(nodelist.compound_statement, level+1)

        elif isinstance(nodelist, ast.ParameterTypeList):
            for paramdec in nodelist.nodes:
                decl_param = self.analyze_param_declaration(paramdec, level)
                if self.env.lookup(decl_param.name) == None:
                    print("OK: No duplication in environment.")
                    self.env.add(decl_param)
                else:
                    existing_decl = self.env.lookup(decl_param.name)
                    if existing_decl.kind == "param":
                        if existing_decl.level != 1:
                            sys.stderr.write("Unexpected parameter duplication - {0}.\n".format(decl_param.name))
                        else:
                            sys.stderr.write("Error: This parameter declaration is duplicated - param {0}\n".format(decl_param.name))
                    else:
                        self.env.add(decl_param)
                print("")

        elif isinstance(nodelist, ast.CompoundStatement):
            print("Analyzing compound statement...")
            for declaration in nodelist.declaration_list.nodes:
                self.analyze(declaration, level)
                print("Declaration in compound statement {0}".format(type(declaration)))
            for statement in nodelist.statement_list.nodes:
                self.analyze(statement, level)
                print("Statement in compound statement {0}".format(type(statement)))

        elif isinstance(nodelist, ast.DeclaratorList):
            for declaration in nodelist.nodes:
                self.analyze(declaration, level)

        elif isinstance(nodelist, ast.StatementList):
            for statement in nodelist.nodes:
                self.analyze(statement, level)

        elif isinstance(nodelist, ast.ExpressionStatement):
            print("Analyze expression.")
            print("")

        elif isinstance(nodelist, ast.IfStatement):
            print("Analyze if statement.")
            print("")

        elif isinstance(nodelist, ast.WhileLoop):
            print("Analyze while statement.")
            print("")

        elif isinstance(nodelist, ast.ForLoop):
            print("Analyze for statement.")
            print("")

        elif isinstance(nodelist, ast.ReturnStatement):
            print("Analyze return statement.")
            print("")


        return self.env
