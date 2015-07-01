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
        # self.scope = []

    def add(self, decl):
        self.decl_list.append(decl)

    # if the object which has the same name is found, return the Decl class
    # object, otherwise return None
    def lookup(self, name, index=0):
        for decl in self.decl_list[index:]:
            if name == decl.name:
                return decl


class Analyzer(object):

    def __init__(self, ast_top):
        self.nodelist = ast_top
        self.env = Environment()
        # self.last = False
        self.error_msg = ""
        self.warning_msg = ""
        self.error_count = 0
        self.warning_count = 0

    # generate Decl object
    # for ast.Declaration
    def analyze_declaration(self, declaration_node, declarator, level):
        print("Begin analyzing declaration.")
        # 抽象構文木をたどって変数名を取ってくる
        name = declarator.direct_declarator.identifier.identifier
        print("{0}".format(name))

        # void型変数をはねる(型検査を埋め込み)
        if declaration_node.type_specifier.type_specifier == "void":
            self.error_msg += "Error - Type of variable {0} must not be \"void\" at line {1}.\n".format(
                name, declarator.direct_declarator.identifier.lineno)
            self.error_count += 1

        if declarator.kind == "NORMAL":
            if isinstance(declarator.direct_declarator, ast.DirectDeclarator):
                objtype = "int"
            elif isinstance(declarator.direct_declarator, ast.DirectArrayDeclarator):
                objtype = (
                    "array", "int", declarator.direct_declarator.constant.value)
        elif declarator.kind == "POINTER":
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
            sys.stderr.write(
                "Prototype function declaration is available only at top-level.\n")
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
                        objtype.append(
                            ("pointer", param.type_specifier.type_specifier))

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
            sys.stderr.write(
                "Function definition is available only at top-level.\n")
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
                        objtype.append(
                            ("pointer", param.type_specifier.type_specifier))

        decl_funcdef = Decl(name, level, kind, tuple(objtype))

        # for debug
        print(
            "new Decl class object of function definition: {0}".format(decl_funcdef))
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
        print(
            "new Decl class object of parameter declaration: {0}".format(decl_param))
        print("name: {0}".format(decl_param.name))
        print("level: {0}".format(decl_param.level))
        print("kind: {0}".format(decl_param.kind))
        print("type: {0}".format(decl_param.objtype))

        return decl_param

    def analyze(self, nodelist, level=0, scope_index=0):
        if isinstance(nodelist, ast.ExternalDeclarationList):
            print("Analyze nodes in external declaration list.")
            for node in nodelist.nodes:
                self.analyze(node, level)

        elif isinstance(nodelist, ast.Declaration):
            # vardecl_list = []
            for declarator in nodelist.declarator_list.nodes:
                decl_decl = self.analyze_declaration(
                    nodelist, declarator, level)

                # # 修正版重複チェック
                # for decl_into_env int vardecl_list:
                #     if decl_decl.name == decl_into_env.name:
                #         if existing_decl.kind == "fun" or existing_decl.kind == "proto":
                #             if existing_decl.level == 0:
                #                 self.error_msg += "Error - {0} is defined as a function.\n".format(
                #                     decl_decl.name)
                #                 self.error_count += 1
                #             else:
                #                 self.env.add(decl_decl)
                #         elif existing_decl.kind == "var":
                #             if existing_decl.level == decl_decl.level:
                #                 self.error_msg += "Error - Duplicate declaration - {0}\n".format(
                #                     decl_decl.name)
                #                 self.error_count += 1
                #         elif existing_decl.kind == "param":
                #             self.env.add(decl_decl)
                #             self.warning_msg += "Warning - This variable declaration is duplicated - param {0}".format(
                #                 existing_decl.name)
                #             self.warning_count += 1

                # ここから修正
                if self.env.lookup(decl_decl.name, scope_index) is None:
                    print("OK - No duplication in environment.")
                    self.env.add(decl_decl)
                else:
                    existing_decl = self.env.lookup(
                        decl_decl.name, scope_index)
                    if existing_decl.kind == "fun" or existing_decl.kind == "proto":
                        if existing_decl.level == 0:
                            self.error_msg += "Error - {0} is defined as a function.\n".format(
                                decl_decl.name)
                            self.error_count += 1
                        else:
                            self.env.add(decl_decl)
                    elif existing_decl.kind == "var":
                        if existing_decl.level == decl_decl.level and self.env.decl_list.index(existing_decl):
                            self.error_msg += "Error - Duplicate declaration - {0}\n".format(
                                decl_decl.name)
                            self.error_count += 1
                    elif existing_decl.kind == "param":
                        self.env.add(decl_decl)
                        self.warning_msg += "Warning - This variable declaration is duplicated - param {0}\n".format(
                            existing_decl.name)
                        self.warning_count += 1
                print("")

        elif isinstance(nodelist, ast.FunctionPrototype):
            decl_proto = self.analyze_func_prototype(nodelist, level)
            if self.env.lookup(decl_proto.name) is None:
                print("OK - No duplication in environment.")
                self.env.add(decl_proto)
            else:
                existing_decl = self.env.lookup(decl_proto.name)

                if existing_decl.kind == "fun":
                    if existing_decl.objtype != decl_proto.objtype:
                        self.error_msg += "Error - Conflicting {0} prototype definition with {1} function.\n".format(
                            decl_proto.type, existing_decl.type)
                        self.error_count += 1
                    else:
                        print(
                            "OK: Prototype declaration after function definition, type consisntent")
                        self.env.add(decl_proto)
                elif existing_decl.kind == "proto":
                    if existing_decl.objtype[1] != decl_proto.objtype[1]:
                        self.error_msg += "Error - Type inconsintency of duplicate prototype definition - {0}\n".format(
                            decl_proto.name)
                        self.error_count += 1
                    else:
                        print(
                            "OK: Duplicate prototype declaration, but type consistent")
                        self.env.add(decl_proto)
                elif existing_decl.kind == "var":
                    if existing_decl.level == 0:
                        self.error_msg += "Error - Duplicate prototype declaration with global variable: {0}\n".format(
                            decl_proto.name)
                        self.error_count += 1
                    else:
                        print(
                            "OK: Duplicate prototype declaration and variable declaration, but they are at different level.")
                        self.env.add(decl_proto)

            print("")
            self.analyze(
                nodelist.function_declarator.parameter_type_list, level+1)

        elif isinstance(nodelist, ast.FunctionDefinition):
            decl_funcdef = self.analyze_func_definition(nodelist, level)
            if self.env.lookup(decl_funcdef.name) is None:
                print("OK: No duplication in environment.")
                self.env.add(decl_funcdef)
            else:
                existing_decl = self.env.lookup(decl_funcdef.name)

                if existing_decl.kind == "fun":
                    self.error_msg += "Error - Duplicate function definition - {0}.\n".format(
                        decl_funcdef.name)
                    self.error_count += 1
                elif existing_decl.kind == "proto":
                    if existing_decl.objtype != decl_funcdef.objtype:
                        self.error_msg += "Error - Type inconsintency of function prototype and function definition - {0}\n".format(
                            decl_funcdef.name)
                        self.error_count += 1
                    else:
                        print(
                            "OK: Types of prototype and function definition are consistent")
                        self.env.add(decl_funcdef)
                elif existing_decl.kind == "var":
                    if existing_decl.level == 0:
                        self.error_msg += "Error - Duplicate function definition with global variable - {0}\n".format(
                            decl_funcdef.name)
                        self.error_count += 1
                    else:
                        print(
                            "OK: Duplicate function definition and variable declaration, but they are at different level.")
                        self.env.add(decl_funcdef)

            print("")
            func_index = self.env.decl_list.index(decl_funcdef)
            print("Func index: {0}".format(func_index))
            print("Begin analyzing parameter in function definition.")
            self.analyze(
                nodelist.function_declarator.parameter_type_list, level+1, func_index)
            print("Begin analyzing compound statement in function definition.")
            self.analyze(nodelist.compound_statement, level+2, func_index)

        elif isinstance(nodelist, ast.ParameterTypeList):
            param_list = []

            for paramdec in nodelist.nodes:
                decl_param = self.analyze_param_declaration(paramdec, level)

                # 重複チェック
                for param_into_env in param_list:
                    if decl_param.name == param_into_env.name:
                        self.error_msg += "Error - This parameter declaration is duplicated - param {0}\n".format(
                            decl_param.name)
                        self.error_count += 1
                param_list.append(decl_param)
                print("")

            # 重複のなかったパラメータ宣言を環境に登録
            for param in param_list:
                self.env.add(param)

        elif isinstance(nodelist, ast.CompoundStatement):
            print("Analyzing compound statement...")

            for declaration in nodelist.declaration_list.nodes:
                print(
                    "Declaration in compound statement {0}".format(type(declaration)))
                self.analyze(declaration, level, scope_index)

            for statement in nodelist.statement_list.nodes:
                print(
                    "Statement in compound statement {0}".format(type(statement)))
                self.analyze(statement, level)

        elif isinstance(nodelist, ast.DeclarationList):
            for declaration in nodelist.nodes:
                print("Analyzing declaration {0}...".format(declaration))
                self.analyze(declaration, level, scope_index)

        elif isinstance(nodelist, ast.StatementList):
            for statement in nodelist.nodes:
                self.analyze(statement, level, scope_index)

        elif isinstance(nodelist, ast.ExpressionStatement):
            print("Analyze expression.")
            # print(type(nodelist.expression))
            self.analyze(nodelist.expression)

        elif isinstance(nodelist, ast.FunctionExpression):
            if self.env.lookup(nodelist.identifier.identifier) is None:
                self.error_msg += "Error - Referencing undeclared function {0} at line {1}.\n".format(
                    nodelist.identifier.identifier, nodelist.lineno)
                self.error_count += 1
            else:
                existing_decl = self.env.lookup(
                    (nodelist.identifier.identifier))
                if existing_decl.kind == "fun":
                    print("Successed calling function {0}.".format(
                        nodelist.identifier.identifier))
                    nodelist.identifier = existing_decl
                elif existing_decl.kind == "var" or existing_decl.kind == "param":
                    self.error_msg += "Error - Referencing variable {0} as a function at line {1}.\n".format(
                        nodelist.identifier.identifier, nodelist.lineno)
                    self.error_count += 1

        elif isinstance(nodelist, ast.BinaryOperators):
            self.analyze(nodelist.left, level)
            self.analyze(nodelist.right, level)
            print(
                "Type of left-hand side expression: {0}".format(nodelist.left.identifier))

            if isinstance(nodelist.left.identifier, Decl):
                print(
                    "left-hand side is Decl class! - {0}".format(nodelist.left.identifier.name))
                binop_left = self.env.lookup(nodelist.left.identifier.name)
            else:
                binop_left = self.env.lookup(nodelist.left.identifier)

            if nodelist.op == "ASSIGN":
                if not binop_left.kind == "var":
                    self.error_msg += "Error - Invalid type at left-hand side of assignment: {0} at line {1}\n".format(
                        binop_left.name, nodelist.left.lineno)
                    self.error_count += 1
                elif binop_left.objtype[0] == "array":
                    self.error_msg += "Error - Variable at left-hand side of assignment must not be array type: line {0}\n".format(
                        nodelist.left.lineno)
                    self.error_count += 1

        elif isinstance(nodelist, ast.Address):
            self.analyze(nodelist.expression, level)
            print("Checking operand of pointer...")

            exp = self.env.lookup(nodelist.expression.identifier)
            if exp.kind != "var":
                self.error_msg += "Error - Illegal operand of pointer.\n"
                self.error_count += 1

        elif isinstance(nodelist, ast.Pointer):
            self.analyze(nodelist.expression, level)

        elif isinstance(nodelist, ast.Identifier):
            if self.env.lookup(nodelist.identifier) is None:
                self.error_msg += "Error - Referencing undeclared variable {0} at line {1}.\n".format(
                    nodelist.identifier, nodelist.lineno)
                self.error_count += 1
            else:
                existing_decl = self.env.lookup((nodelist.identifier))

                if existing_decl.kind == "fun":
                    self.error_msg += "Error - Referencing function {0} as a variable at {1}.\n".format(
                        nodelist.identifier, nodelist.lineno)
                    self.error_count += 1
                elif existing_decl.kind == "var" or existing_decl.kind == "param":
                    print(
                        "Successed referencing variable {0}.".format(nodelist.identifier))
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
        print("Type check.")
        print("Env length: {0}".format(len(self.env.decl_list)))
        if isinstance(nodelist, ast.NullNode):
            pass

        # top level
        elif isinstance(nodelist, ast.ExternalDeclarationList):
            print("Checking type of external declaration.")
            print(type(nodelist.nodes))
            print(len(nodelist.nodes))
            for count, node in enumerate(nodelist.nodes):
                print("Checking respective node of external declaration.")
                # if count == len(nodelist.nodes)-1:
                    # self.last = True
                self.check_type(node, env)

        # declaration
        elif isinstance(nodelist, ast.Declaration):
            print("Checking type of declaration.")
            self.check_type(nodelist.declarator_list, env)

        elif isinstance(nodelist, ast.DeclaratorList):
            print("Checking type of declarator list.")
            for declarator in nodelist.nodes:
                self.check_type(declarator, env)

        elif isinstance(nodelist, ast.Declarator):
            print("Checking type of declarator.")
            self.check_type(nodelist.direct_declarator, env)

        elif isinstance(nodelist, ast.DirectDeclarator):
            print("Checking type of direct declarator.")
            decl = env.lookup(nodelist.identifier.identifier.name)
            # if not decl.kind == "var":
            #     self.error_msg += "Error - Illegal type of declaration at line {0}: variable {1}\n".format(
            #         nodelist.identifier.lineno, nodelist.identifier.identifier.name)
            #     self.error_count += 1

        elif isinstance(nodelist, ast.FunctionPrototype):
            pass

        elif isinstance(nodelist, ast.FunctionDefinition):
            print("Type check of function definition {0}...".format(
                nodelist.function_declarator.identifier.identifier))

            # 返り値の型の整合性チェック
            for stmtlist in nodelist.compound_statement.statement_list.nodes:
                for stmt_node in stmtlist.nodes:
                    # return文を探す
                    if isinstance(stmt_node, ast.ReturnStatement):
                        # void
                        if isinstance(stmt_node.return_statement, ast.NullNode):
                            if nodelist.type_specifier.type_specifier == "int":
                                self.error_msg += "Error - Void-type return but int-type function definition {0} at line {1}.\n".format(
                                    nodelist.function_declarator.identifier.identifier, nodelist.function_declarator.identifier.lineno)
                                self.error_count += 1
                        else:
                            if nodelist.type_specifier.type_specifier == "void":
                                self.error_msg += "Error - Int-type return but void-type function definition {0} at line {1}.\n".format(
                                    nodelist.function_declarator.identifier.identifier, nodelist.function_declarator.identifier.lineno)
                                self.error_count += 1
            else:  # return文がなかったとき
                if nodelist.type_specifier.type_specifier == "int":
                    self.error_msg += "Error - Void-type return but int-type function definition {0} at line {1}.\n".format(
                        nodelist.function_declarator.identifier.identifier, nodelist.function_declarator.identifier.lineno)
                    self.error_count += 1

            # 関数定義内の複文の型チェック
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
            print("Checking type of expression statement.")
            self.check_type(nodelist.expression, env)

        elif isinstance(nodelist, ast.IfStatement):
            print("Checking type of if statement.")
            if not self.check_type(nodelist.expression, env) == "int":
                self.error_msg += "Error - Expression of if statement must return int-type.\n"
                self.error_count += 1
            self.check_type(nodelist.then_statement, env)
            self.check_type(nodelist.else_statement, env)

        elif isinstance(nodelist, ast.WhileLoop):
            print("Checking type of while statement.")
            if not self.check_type(nodelist.expression) == "int":
                self.error_msg += "Error - Expression of while statement must return int-type.\n"
                self.error_count += 1
            self.check_type(nodelist.statement, env)

        elif isinstance(nodelist, ast.ReturnStatement):
            print("Checking type of return statement.")
            self.check_type(nodelist.return_statement, env)

        elif isinstance(nodelist, ast.BinaryOperators):
            if nodelist.op == "ASSIGN":
                print("Checking type of assign expression.")
                if self.check_type(nodelist.left, env) == self.check_type(nodelist.right, env):
                    return self.check_type(nodelist.left, env)
                else:
                    self.error_msg += "Error - Type inconsintency between left-hand and right-hand of assign expression.\n"
                    self.error_count += 1

            elif nodelist.op == "AND" or nodelist.op == "OR":
                print("Checking type of and-or expression.")
                if self.check_type(nodelist.left, env) == "int" and self.check_type(nodelist.right, env) == "int":
                    return "int"
                else:
                    self.error_msg += "Error - Type inconsisntency of logical expression.\n"
                    self.error_count += 1

            elif nodelist.op == "EQUAL" \
                    or nodelist.op == "NEQ" \
                    or nodelist.op == "LT" \
                    or nodelist.op == "GT" \
                    or nodelist.op == "LEQ" \
                    or nodelist.op == "GEQ":
                print("Checking type of equality expression.")
                if self.check_type(nodelist.left, env) == self.check_type(nodelist.right, env):
                    return "int"
                else:
                    self.error_msg += "Error - Type inconsintency between left-hand and right-hand of assign expression.\n"
                    self.error_count += 1

            elif nodelist.op == "PLUS" \
                    or nodelist.op == "TIMES" \
                    or nodelist.op == "DIVIDE":
                print("Checking type of calculation expression.")
                if self.check_type(nodelist.left, env) == self.check_type(nodelist.right, env) == "int":
                    return "int"
                elif self.check_type(nodelist.left, env) == "int" and self.check_type(nodelist.right, env) == ("pointer", "int") \
                        or self.check_type(nodelist.left, env) == ("pointer", "int") and self.check_type(nodelist.right, env) == "int":
                    return ("pointer", "int")
                else:
                    self.error_msg += "Error - Type inconsintency of calculation operands.\n"
                    self.error_count += 1

            elif nodelist.op == "MINUS":
                print("Checking type of minus expression.")
                if self.check_type(nodelist.left, env) == self.check_type(nodelist.right, env) == "int":
                    return "int"
                elif self.check_type(nodelist.left, env) == ("pointer", "int") and self.check_type(nodelist.right, env) == "int":
                    return ("pointer", "int")
                else:
                    self.error_msg += "Error - Type inconsintency of calculation operands.\n"
                    self.error_count += 1

        elif isinstance(nodelist, ast.Address):
            print("Checking type of address expression.")
            if self.check_type(nodelist.expression, env) == "int":
                return ("pointer", "int")
            else:
                self.error_msg += "Error - Invalid type for operand of pointer expression.\n"
                self.error_count += 1

        elif isinstance(nodelist, ast.FunctionExpression):
            print("Checking type of function call.")
            func_decl = self.env.lookup(nodelist.identifier.identifier)
            # 引数の個数チェック
            if isinstance(nodelist.argument_expression, ast.NullNode):
                arglen = 0
            else:
                arglen = len(nodelist.argument_expression.nodes)
            if arglen > len(func_decl.objtype[2:]):
                self.error_msg += "Error - Too many arguments for function {0}.\n".format(
                    func_decl.name)
                self.error_count += 1
            elif arglen < len(func_decl.objtype[2:]):
                self.error_msg += "Error - Too few arguments for function {0}.\n".format(
                    func_decl.name)
                self.error_count += 1
            else:  # 引数の個数が一致したとき
                # 引数の型チェック
                if arglen == 0:
                    return func_decl.objtype[1]
                else:
                    for i, argnode in enumerate(nodelist.argument_expression.nodes):
                        if not self.check_type(argnode, env) == func_decl.objtype[2+i]:
                            ill_type = self.check_type(argnode, env)
                            self.error_msg += "Error - Taking {0} type argument for function {1}: correct type is {2}.\n".format(
                                ill_type, func_decl.name. func_decl.objtype[2+i])
                            self.error_count += 1
                    else:
                        return func_decl.objtype[1]

        elif isinstance(nodelist, ast.Identifier):
            print("Checking type of identifier.")
            if isinstance(nodelist.identifier, Decl):
                print("Checking type of identifier {0} ...".format(
                    nodelist.identifier.name))
                id_decl = self.env.lookup(nodelist.identifier.name)
            else:
                print(
                    "Checking type of identifier {0} ...".format(nodelist.identifier))
                id_decl = self.env.lookup(nodelist.identifier)
            if id_decl.objtype == "int":
                return "int"
            else:
                return ("pointer", "int")

        elif isinstance(nodelist, ast.Number):
            print("Checking type of number.")
            return "int"

        # 最後にエラー出力
        # if self.last:
            # self.print_error()

        return self.error_msg, self.warning_msg, self.error_count, self.warning_count


class ErrorManager(object):

    def __init__(self, e_msg, w_msg, e_cnt, w_cnt):
        self.error_msg = e_msg
        self.warning_msg = w_msg
        self.error_count = e_cnt
        self.warning_count = w_cnt

    def print_error(self):
        print("{0} Errors and {1} Warnings.".format(
            self.error_count, self.warning_count))

        if not self.warning_msg == "":
            sys.stderr.write(self.warning_msg)

        if not self.error_msg == "":
            # 後々sys.exit(...)に書き換える
            sys.stderr.write(self.error_msg)
