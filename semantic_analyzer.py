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
        self.parent_func = None

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

            objtype = ["fun", return_type]
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
            param_list = []

            for paramdec in nodelist.nodes:
                decl_param = self.analyze_param_declaration(paramdec, level)
                # if self.env.lookup(decl_param.name) == None:
                #     print("OK: No duplication in environment.")
                #     self.env.add(decl_param)
                # else:
                #     existing_decl = self.env.lookup(decl_param.name)
                #     if existing_decl.kind == "param":
                #         if existing_decl.level != 1:
                #             sys.stderr.write("Unexpected parameter duplication - {0}.\n".format(decl_param.name))
                #         else:
                #             sys.stderr.write("Error: This parameter declaration is duplicated - param {0}\n".format(decl_param.name))
                #     else:
                #         self.env.add(decl_param)

                # 重複チェック
                for param_into_env in param_list:
                    if decl_param.name == param_into_env.name:
                        sys.stderr.write("Error: This parameter declaration is duplicated - param {0}\n".format(decl_param.name))
                param_list.append(decl_param)
                print("")

            # 重複のなかったパラメータ宣言を環境に登録
            for param in param_list:
                self.env.add(param)


        elif isinstance(nodelist, ast.CompoundStatement):
            print("Analyzing compound statement...")

            for declaration in nodelist.declaration_list.nodes:
                print("Declaration in compound statement {0}".format(type(declaration)))
                self.analyze(declaration, level)

            for statement in nodelist.statement_list.nodes:
                print("Statement in compound statement {0}".format(type(statement)))
                self.analyze(statement, level)


        elif isinstance(nodelist, ast.DeclarationList):
            for declaration in nodelist.nodes:
                print("Analyzing declaration {0}...".format(declaration))
                self.analyze(declaration, level)


        elif isinstance(nodelist, ast.StatementList):
            for statement in nodelist.nodes:
                self.analyze(statement, level)


        elif isinstance(nodelist, ast.ExpressionStatement):
            print("Analyze expression.")
            # print(type(nodelist.expression))
            self.analyze(nodelist.expression)


        elif isinstance(nodelist, ast.FunctionExpression):
            if self.env.lookup(nodelist.identifier.identifier) == None:
                sys.stderr.write("Error - Referencing undeclared function {0} at line {1}.\n".format(nodelist.identifier.identifier, nodelist.lineno))
            else:
                existing_decl = self.env.lookup((nodelist.identifier.identifier))
                if existing_decl.kind == "fun":
                    print("Successed calling function {0}.".format(nodelist.identifier.identifier))
                    nodelist.identifier = existing_decl
                elif existing_decl.kind == "var" or existing_decl.kind == "param":
                    sys.stderr.write("Error - Referencing variable {0} as a function at line {1}.".format(nodelist.identifier.identifier, nodelist.lineno))


        elif isinstance(nodelist, ast.BinaryOperators):
            self.analyze(nodelist.left, level)
            self.analyze(nodelist.right, level)
            print("Type of left-hand side expression: {0}".format(nodelist.left.identifier))

            if isinstance(nodelist.left.identifier, Decl):
                print("left-hand side is Decl class! - {0}".format(nodelist.left.identifier.name))
                binop_left = self.env.lookup(nodelist.left.identifier.name)
            else:
                binop_left = self.env.lookup(nodelist.left.identifier)

            if nodelist.op == "ASSIGN":
                if not binop_left.kind == "var":
                    sys.stderr.write("Error - Invalid type at left-hand side of assignment: {0} at line {1}".format(binop_left.name, nodelist.left.lineno))
                elif binop_left.objtype[0] == "array":
                    sys.stderr.write("Error - Variable at left-hand side of assignment must not be array type: line {0}".format(nodelist.left.lineno))


        elif isinstance(nodelist, ast.Address):
            self.analyze(nodelist.expression, level)
            print("Checking operand of pointer...")

            exp = self.env.lookup(nodelist.expression.identifier)
            if exp.kind != "var":
                sys.stderr.write("Error - Illegal operand of pointer.")


        elif isinstance(nodelist, ast.Pointer):
            self.analyze(nodelist.expression, level)


        elif isinstance(nodelist, ast.Identifier):
            if self.env.lookup(nodelist.identifier) == None:
                sys.stderr.write("Error - Referencing undeclared variable {0} at line {1}.\n".format(nodelist.identifier, nodelist.lineno))
            else:
                existing_decl = self.env.lookup((nodelist.identifier))
                if existing_decl.kind == "fun":
                    sys.stderr.write("Error - Referencing function {0} as a variable at {1}.".format(nodelist.identifier, nodelist.lineno))
                elif existing_decl.kind == "var" or existing_decl.kind == "param":
                    print("Successed referencing variable {0}.".format(nodelist.identifier))
                    nodelist.identifier = existing_decl


        elif isinstance(nodelist, ast.IfStatement):
            print("Analyze if statement.")
            self.analyze(nodelist.expression, level+1)
            self.analyze(nodelist.then_statement, level+1)
            self.analyze(nodelist.else_statement, level+1)


        elif isinstance(nodelist, ast.WhileLoop):
            print("Analyze while statement.")
            self.analyze(nodelist.expression, level+1)
            self.analyze(nodelist.statement, level+1)


        elif isinstance(nodelist, ast.ForLoop):
            print("Analyze for statement.")
            self.analyze(nodelist.firstexp_statement, level)
            self.analyze(nodelist.whileloop_node, level)


        elif isinstance(nodelist, ast.ReturnStatement):
            print("Analyze return statement.")
            self.analyze(nodelist.return_statement, level)


        return self.env


    # 型検査のための関数
    def check_type(self, nodelist, env):
        if isinstance(nodelist, ast.NullNode):
            pass

        # top level
        elif isinstance(nodelist, ast.ExternalDeclarationList):
            for node in nodelist.nodes:
                self.check_type(node, env)

        # declaration
        elif isinstance(nodelist, ast.Declaration):
            self.check_type(nodelist.declarator_list, env)

        elif isinstance(nodelist, ast.DeclaratorList):
            for declarator in nodelist.nodes:
                self.check_type(declarator, env)

        elif isinstance(nodelist, ast.Declarator):
            self.check_type(nodelist.direct_declarator, env)

        elif isinstance(nodelist, ast.DirectDeclarator):
            # print("Type: {0}".format(type(nodelist.identifier.identifier)))
            # self.env.lookup(nodelist.identifier.identifier)
            decl = env.lookup(nodelist.identifier.identifier.name)
            if not decl.kind == "var":
                sys.stderr.write("Error - Illigal type of declaration at line {0}: variable {1}".format(nodelist.identifier.lineno, nodelist.identifier.identifier.name))

        elif isinstance(nodelist, ast.FunctionPrototype):
            pass

        elif isinstance(nodelist, ast.FunctionDefinition):
            self.parent_func = nodelist
            self.check_type(nodelist.compound_statement, env)

        elif isinstance(nodelist, ast.CompoundStatement):
            self.check_type(nodelist.declaration_list, env)
            self.check_type(nodelist.statement_list, env)

        elif isinstance(nodelist, ast.DeclarationList):
            for node in nodelist.nodes:
                self.check_type(node, env)

        elif isinstance(nodelist, ast.StatementList):
            for node in nodelist.nodes:
                self.check_type(node, env)

        elif isinstance(nodelist, ast.ExpressionStatement):
            self.check_type(nodelist.expression, env)

        elif isinstance(nodelist, ast.IfStatement):
            self.check_type(nodelist.expression, env)
            self.check_type(nodelist.then_statement, env)
            self.check_type(nodelist.else_statement, env)

        elif isinstance(nodelist, ast.WhileLoop):
            self.check_type(nodelist.expression)
            self.check_type(nodelist.statement, env)

        elif isinstance(nodelist, ast.ReturnStatement):
            print("Return: parent ... {0}".format(self.parent_func.function_declarator.identifier.identifier))
            func_env = env.lookup(self.parent_func.function_declarator.identifier.identifier)
            print("Searched env and name is {0} and type is {1}".format(func_env.name, func_env.objtype))

            if isinstance(nodelist.return_statement, ast.NullNode):
                if func_env.objtype[1] == "int":
                    sys.stderr.write("Error - Type inconsintency between function definition and return statement at {0} - {1} and {2}.".format(self.parent_func.function_declarator.identifier.lineno, self.parent_func.function_declarator.identifier.identifier, func_env.name))

            else:
                if func_env.objtype[1] == "void":
                    sys.stderr.write("Error - Type inconsintency between function definition and return statement at line {0} - {1} and {2}.".format(self.parent_func.function_declarator.identifier.lineno, self.parent_func.function_declarator.identifier.identifier, func_env.name))

        elif isinstance(nodelist, ast.BinaryOperators):
            pass
