#!/usr/bin/python
# -*- coding: utf-8 -*-

"""意味解析モジュール"""

import sys
import ast
import logging


class Decl(object):

    def __init__(self, name, level, kind, objtype, offset=0):
        self.name = name
        self.level = level
        self.kind = kind
        self.objtype = objtype
        self.offset = offset

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


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
        # self.error_msg = ""
        # self.warning_msg = ""
        self.error_count = 0
        self.warning_count = 0

    # generate Decl object
    # for ast.Declaration
    def analyze_declaration(self, declaration_node, declarator, level):
        # 抽象構文木をたどって変数名を取ってくる
        name = declarator.direct_declarator.identifier.identifier

        # void型変数をはねる(型検査を埋め込み)
        if declaration_node.type_specifier.type_specifier == "void":
            logging.error("Type of variable {0} must not be \"void\" at line {1}.".format(
                name, declarator.direct_declarator.identifier.lineno))
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
        declarator.direct_declarator.identifier.identifier = decl_decl

        return decl_decl

    def analyze_statement(self, statement_node, level):
        pass

    def analyze_func_prototype(self, proto_node, level):
        if level != 0:
            logging.error(
                "Prototype function declaration is available only at top-level.")
            self.error_count += 1
        else:
            # 抽象構文木をたどって関数名を取ってくる
            name = proto_node.function_declarator.identifier.identifier

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

        return decl_proto

    def analyze_func_definition(self, funcdef_node, level):
        if level != 0:
            logging.error(
                "Function definition is available only at top-level.")
            error_count += 1
        else:
            # 抽象構文木をたどって関数名を取ってくる
            name = funcdef_node.function_declarator.identifier.identifier
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

        return decl_funcdef

    def analyze_param_declaration(self, paramdec_node, level):
        # 抽象構文木をたどってパラメータ宣言を取ってくる
        name = paramdec_node.parameter_declarator.identifier.identifier

        if paramdec_node.parameter_declarator.kind == "NORMAL":
            objtype = "int"
        elif paramdec_node.parameter_declarator.kind == "POINTER":
            objtype = ("pointer", "int")

        decl_param = Decl(name, level, "param", objtype)

        return decl_param

    def analyze(self, nodelist, level=0, scope_index=0):
        if isinstance(nodelist, ast.ExternalDeclarationList):
            for node in nodelist.nodes:
                self.analyze(node, level)

        elif isinstance(nodelist, ast.Declaration):
            for declarator in nodelist.declarator_list.nodes:
                decl_decl = self.analyze_declaration(
                    nodelist, declarator, level)

                if self.env.lookup(decl_decl.name, scope_index) is None:
                    self.env.add(decl_decl)
                else:
                    existing_decl = self.env.lookup(
                        decl_decl.name, scope_index)
                    if existing_decl.kind == "fun" or existing_decl.kind == "proto":
                        if existing_decl.level == 0:
                            logging.error("{0} is defined as a function.".format(
                                decl_decl.name))
                            self.error_count += 1
                        else:
                            self.env.add(decl_decl)
                    elif existing_decl.kind == "var":
                        if existing_decl.level == decl_decl.level:
                            logging.error("Duplicate declaration - {0}".format(
                                decl_decl.name))
                            self.error_count += 1
                    elif existing_decl.kind == "param":
                        self.env.add(decl_decl)
                        logging.warning("This variable declaration is duplicated - param {0}".format(
                            existing_decl.name))
                        self.warning_count += 1

        elif isinstance(nodelist, ast.FunctionPrototype):
            decl_proto = self.analyze_func_prototype(nodelist, level)
            nodelist.function_declarator.identifier.identifier = decl_proto
            if self.env.lookup(decl_proto.name) is None:
                self.env.add(decl_proto)
            else:
                existing_decl = self.env.lookup(decl_proto.name)

                if existing_decl.kind == "fun":
                    if existing_decl.objtype != decl_proto.objtype:
                        logging.error("Conflicting {0} prototype definition with {1} function.".format(
                            decl_proto.type, existing_decl.type))
                        self.error_count += 1
                    else:
                        self.env.add(decl_proto)
                elif existing_decl.kind == "proto":
                    if existing_decl.objtype[1] != decl_proto.objtype[1]:
                        logging.error("Type inconsintency of duplicate prototype definition - {0}".format(
                            decl_proto.name))
                        self.error_count += 1
                    else:
                        self.env.add(decl_proto)
                elif existing_decl.kind == "var":
                    if existing_decl.level == 0:
                        logging.error("Duplicate prototype declaration with global variable: {0}".format(
                            decl_proto.name))
                        self.error_count += 1
                    else:
                        self.env.add(decl_proto)

            # self.analyze(
                # nodelist.function_declarator.parameter_type_list, level+1)

            param_list = []

            for paramdec in nodelist.function_declarator.parameter_type_list.nodes:
                decl_param = self.analyze_param_declaration(paramdec, level)

                # 重複チェック
                for existing_param in param_list:
                    if decl_param.name == existing_param.name:
                        logging.error("This parameter declaration in function prototype declaration is duplicated - param {0}".format(
                            decl_param.name))
                        self.error_count += 1
                param_list.append(decl_param)

        elif isinstance(nodelist, ast.FunctionDefinition):
            decl_funcdef = self.analyze_func_definition(nodelist, level)
            nodelist.function_declarator.identifier.identifier = decl_funcdef

            if self.env.lookup(decl_funcdef.name) is None:
                self.env.add(decl_funcdef)
            else:
                existing_decl = self.env.lookup(decl_funcdef.name)

                if existing_decl.kind == "fun":
                    logging.error("Duplicate function definition - {0}.".format(
                        decl_funcdef.name))
                    self.error_count += 1
                elif existing_decl.kind == "proto":
                    if existing_decl.objtype != decl_funcdef.objtype:
                        logging.error("Type inconsintency of function prototype and function definition - {0}".format(
                            decl_funcdef.name))
                        self.error_count += 1
                    else:
                        self.env.add(decl_funcdef)
                elif existing_decl.kind == "var":
                    if existing_decl.level == 0:
                        logging.error("Duplicate function definition with global variable - {0}".format(
                            decl_funcdef.name))
                        self.error_count += 1
                    else:
                        self.env.add(decl_funcdef)

            try:
                func_index = self.env.decl_list.index(decl_funcdef)
                self.analyze(
                    nodelist.function_declarator.parameter_type_list, level+1, func_index)
                self.analyze(nodelist.compound_statement, level+2, func_index)
            except ValueError:
                pass

        elif isinstance(nodelist, ast.ParameterTypeList):
            param_list = []

            for paramdec in nodelist.nodes:
                decl_param = self.analyze_param_declaration(paramdec, level)

                # 重複チェック
                for param_into_env in param_list:
                    if decl_param.name == param_into_env.name:
                        logging.error("This parameter declaration is duplicated - param {0}".format(
                            decl_param.name))
                        self.error_count += 1
                param_list.append(decl_param)

            # 重複のなかったパラメータ宣言を環境に登録
            for param in param_list:
                self.env.add(param)

            for paramdec in nodelist.nodes:
                self.analyze(paramdec.parameter_declarator.identifier, level)

        elif isinstance(nodelist, ast.CompoundStatement):
            for declaration in nodelist.declaration_list.nodes:
                self.analyze(declaration, level, scope_index)

            for statement in nodelist.statement_list.nodes:
                self.analyze(statement, level)

        elif isinstance(nodelist, ast.DeclarationList):
            for declaration in nodelist.nodes:
                self.analyze(declaration, level, scope_index)

        elif isinstance(nodelist, ast.StatementList):
            for statement in nodelist.nodes:
                self.analyze(statement, level, scope_index)

        elif isinstance(nodelist, ast.ExpressionStatement):
            self.analyze(nodelist.expression)

        elif isinstance(nodelist, ast.FunctionExpression):
            # 関数名解析
            if self.env.lookup(nodelist.identifier.identifier) is None:
                logging.error("Referencing undeclared function {0} at line {1}.".format(
                    nodelist.identifier.identifier, nodelist.lineno))
                self.error_count += 1
            else:
                existing_decl = self.env.lookup(
                    (nodelist.identifier.identifier))
                if existing_decl.kind == "fun":
                    nodelist.identifier = existing_decl
                elif existing_decl.kind == "proto" and existing_decl.name == "print":
                    nodelist.identifier = existing_decl
                elif existing_decl.kind == "var" or existing_decl.kind == "param":
                    logging.error("Referencing variable {0} as a function at line {1}.".format(
                        nodelist.identifier.identifier, nodelist.lineno))
                    self.error_count += 1

            # パラメータ解析
            self.analyze(nodelist.argument_expression)

        elif isinstance(nodelist, ast.ArgumentExpressionList):
            for argnode in nodelist.nodes:
                self.analyze(argnode, level)

        elif isinstance(nodelist, ast.BinaryOperators):
            self.analyze(nodelist.left, level)
            self.analyze(nodelist.right, level)

            # 式の形の検査
            if isinstance(nodelist, ast.Identifier):
                binop_left = self.env.lookup(nodelist.left.identifier.name)

                if nodelist.op == "ASSIGN":
                    if not binop_left.kind == "var":
                        logging.error("Invalid type at left-hand side of assignment: {0} at line {1}".format(
                            binop_left.name, nodelist.left.lineno))
                        self.error_count += 1
                    elif binop_left.objtype[0] == "array":
                        logging.error("Variable at left-hand side of assignment must not be array type: line {0}".format(
                            nodelist.left.lineno))
                        self.error_count += 1

        elif isinstance(nodelist, ast.Address):
            self.analyze(nodelist.expression, level)

            # 式の形の検査
            exp = self.env.lookup(nodelist.expression.identifier)
            if exp.kind != "var":
                logging.error("Illegal operand of pointer.")
                self.error_count += 1

        elif isinstance(nodelist, ast.Pointer):
            self.analyze(nodelist.expression, level)

        elif isinstance(nodelist, ast.Identifier):
            if isinstance(nodelist.identifier, unicode):
                id_name = nodelist.identifier
            elif isinstance(nodelist.identifier, Decl):
                id_name = nodelist.identifier.name

            if self.env.lookup(id_name) is None:
                logging.error("Referencing undeclared variable {0} at line {1}.".format(
                    id_name, nodelist.lineno))
                self.error_count += 1
            else:
                existing_decl = self.env.lookup(id_name)

                if existing_decl.kind == "fun":
                    logging.error("Referencing function {0} as a variable at {1}.".format(
                        nodelist.identifier, nodelist.lineno))
                    self.error_count += 1
                elif existing_decl.kind == "var" or existing_decl.kind == "param":
                    nodelist.identifier = existing_decl

        elif isinstance(nodelist, ast.IfStatement):
            self.analyze(nodelist.expression, level+1)
            self.analyze(nodelist.then_statement, level+1)
            self.analyze(nodelist.else_statement, level+1)

        elif isinstance(nodelist, ast.WhileLoop):
            self.analyze(nodelist.expression, level+1)
            self.analyze(nodelist.statement, level+1)

        elif isinstance(nodelist, ast.ForLoop):
            self.analyze(nodelist.firstexp_statement, level)
            self.analyze(nodelist.whileloop_node, level)

        elif isinstance(nodelist, ast.ReturnStatement):
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
            pass

        elif isinstance(nodelist, ast.FunctionPrototype):
            pass

        elif isinstance(nodelist, ast.FunctionDefinition):
            # 返り値の型の整合性チェック
            return_exists = False
            for stmt_node in nodelist.compound_statement.statement_list.nodes:
                # for stmt_node in stmtlist.nodes:
                # return文を探す
                if isinstance(stmt_node, ast.ReturnStatement):
                    return_exists = True
                    # void
                    if isinstance(stmt_node.return_statement, ast.NullNode):
                        if nodelist.type_specifier.type_specifier == "int":
                            logging.error("Void-type return but int-type function definition {0} at line {1}.".format(
                                nodelist.function_declarator.identifier.identifier, nodelist.function_declarator.identifier.lineno))
                            self.error_count += 1
                    else:
                        if nodelist.type_specifier.type_specifier == "void":
                            logging.error("Int-type return but void-type function definition {0} at line {1}.".format(
                                nodelist.function_declarator.identifier.identifier, nodelist.function_declarator.identifier.lineno))
                            self.error_count += 1
            if not return_exists:  # return文がなかったとき
                if nodelist.type_specifier.type_specifier == "int":
                    logging.error("Void-type return but int-type function definition {0} at line {1}.".format(
                        nodelist.function_declarator.identifier.identifier, nodelist.function_declarator.identifier.lineno))
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
            self.check_type(nodelist.expression, env)

        elif isinstance(nodelist, ast.IfStatement):
            if not self.check_type(nodelist.expression, env) == "int":
                logging.error(
                    "Expression of if statement must return int-type.")
                self.error_count += 1
            self.check_type(nodelist.then_statement, env)
            self.check_type(nodelist.else_statement, env)

        elif isinstance(nodelist, ast.WhileLoop):
            if not self.check_type(nodelist.expression, env) == "int":
                logging.error(
                    "Expression of while statement must return int-type.")
                self.error_count += 1
            self.check_type(nodelist.statement, env)

        elif isinstance(nodelist, ast.ReturnStatement):
            # print(type(nodelist.return_statement))
            self.check_type(nodelist.return_statement, env)

        elif isinstance(nodelist, ast.BinaryOperators):
            if nodelist.op == "ASSIGN":
                if self.check_type(nodelist.left, env) == self.check_type(nodelist.right, env):
                    return self.check_type(nodelist.left, env)
                else:
                    logging.error(
                        "Type inconsintency between left-hand {0} and right-hand {1} of assign expression.".format(nodelist.left, nodelist.right))
                    self.error_count += 1

            elif nodelist.op == "AND" or nodelist.op == "OR":
                if self.check_type(nodelist.left, env) == "int" and self.check_type(nodelist.right, env) == "int":
                    return "int"
                else:
                    logging.error("Type inconsisntency of logical expression.")
                    self.error_count += 1

            elif nodelist.op == "EQUAL" \
                    or nodelist.op == "NEQ" \
                    or nodelist.op == "LT" \
                    or nodelist.op == "GT" \
                    or nodelist.op == "LEQ" \
                    or nodelist.op == "GEQ":
                if self.check_type(nodelist.left, env) == self.check_type(nodelist.right, env):
                    return "int"
                else:
                    logging.error(
                        "Type inconsintency between left-hand and right-hand of assign expression.")
                    self.error_count += 1

            elif nodelist.op == "PLUS" \
                    or nodelist.op == "TIMES" \
                    or nodelist.op == "DIVIDE":
                if self.check_type(nodelist.left, env) == self.check_type(nodelist.right, env) == "int":
                    return "int"
                elif self.check_type(nodelist.left, env) == "int" and self.check_type(nodelist.right, env) == ("pointer", "int") \
                        or self.check_type(nodelist.left, env) == ("pointer", "int") and self.check_type(nodelist.right, env) == "int":
                    return ("pointer", "int")
                else:
                    logging.error(
                        "Type inconsintency of calculation operands.")
                    self.error_count += 1

            elif nodelist.op == "MINUS":
                if self.check_type(nodelist.left, env) == self.check_type(nodelist.right, env) == "int":
                    return "int"
                elif self.check_type(nodelist.left, env) == ("pointer", "int") and self.check_type(nodelist.right, env) == "int":
                    return ("pointer", "int")
                else:
                    logging.error(
                        "Type inconsintency of calculation operands.")
                    self.error_count += 1

        elif isinstance(nodelist, ast.Address):
            if self.check_type(nodelist.expression, env) == "int":
                return ("pointer", "int")
            else:
                logging.error(
                    "Invalid type for operand of pointer expression.")
                self.error_count += 1

        elif isinstance(nodelist, ast.Pointer):
            if self.check_type(nodelist.expression, env) == ("pointer", "int"):
                return "int"
            else:
                logging.error("Invalid operand of *( ), not a pointer type.")

        elif isinstance(nodelist, ast.FunctionExpression):
            if isinstance(nodelist.identifier, ast.Identifier):
                funcname = nodelist.identifier.identifier
            elif isinstance(nodelist.identifier, Decl):
                funcname = nodelist.identifier.name

            func_decl = self.env.lookup(funcname)
            # 引数の個数チェック
            if isinstance(nodelist.argument_expression, ast.NullNode):
                arglen = 0
            else:
                arglen = len(nodelist.argument_expression.nodes)
                if arglen > len(func_decl.objtype[2:]):
                    logging.error("Too many arguments for function {0}.".format(
                        func_decl.name))
                    self.error_count += 1
                elif arglen < len(func_decl.objtype[2:]):
                    logging.error("Too few arguments for function {0}.".format(
                        func_decl.name))
                    self.error_count += 1
                else:  # 引数の個数が一致したとき
                    # 引数の型チェック
                    if arglen == 0:
                        return func_decl.objtype[1]
                    else:
                        for i, argnode in enumerate(nodelist.argument_expression.nodes):
                            if not self.check_type(argnode, env) == func_decl.objtype[2+i]:
                                ill_type = self.check_type(argnode, env)
                                logging.error("Taking {0} type argument for function {1}: correct type is {2}.".format(
                                    ill_type, func_decl.name. func_decl.objtype[2+i]))
                                self.error_count += 1
                        else:
                            return func_decl.objtype[1]

        elif isinstance(nodelist, ast.Identifier):
            if isinstance(nodelist.identifier, Decl):
                id_decl = self.env.lookup(nodelist.identifier.name)
            else:
                id_decl = self.env.lookup(nodelist.identifier)
            if id_decl.objtype == "int":
                return "int"
            else:
                return ("pointer", "int")

        elif isinstance(nodelist, ast.Number):
            return "int"

        return self.error_count, self.warning_count


class ErrorManager(object):

    def __init__(self, e_cnt, w_cnt):
        # self.error_msg = e_msg
        # self.warning_msg = w_msg
        self.error_count = e_cnt
        self.warning_count = w_cnt

    def print_error(self):
        print("{0} Errors and {1} Warnings.".format(
            self.error_count, self.warning_count))

        # if not self.warning_msg == "":
        #     sys.stderr.write(self.warning_msg)

        # if not self.error_msg == "":
        #     sys.exit(self.error_msg)
