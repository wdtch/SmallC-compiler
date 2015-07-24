#!/usr/bin/python
# -*- coding: utf-8 -*-

"""意味解析モジュール"""

import sys
import ast
import logging


class Decl(object):

    def __init__(self, name, level, kind, objtype, offset=-1):
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
        self.deleted = []

    def add(self, decl):
        self.decl_list.append(decl)

    # if the object which has the same name is found, returns the Decl class
    # object. Otherwise, returns None.
    def lookup(self, name, index=0):
        for decl in reversed(self.decl_list[index:]):
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

    def analyze_declaration(self, declaration_node, declarator, level):
        # 抽象構文木をたどって変数名を取ってくる
        name = declarator.direct_declarator.identifier.identifier

        # void型変数をはねる(型検査を埋め込み)
        if declaration_node.type_specifier.type_specifier == "void":
            logging.error("Line {0}: Type of variable {0} must not be \"void\"".format(
                declarator.direct_declarator.identifier.lineno, name))
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
                objtype = (
                    "pointer", ("array", "int", declarator.direct_declarator.constant.value))

        decl_decl = Decl(name, level, "var", objtype)
        # declarator.direct_declarator.identifier.identifier = decl_decl

        return decl_decl

    # def analyze_statement(self, statement_node, level):
    #     pass

    def analyze_func_prototype(self, proto_node, level):
        if level != 0:
            logging.error(
                "Line {0}: Prototype function declaration is available only at top-level.".format(proto_node.function_declarator.identifier.lineno))
            self.error_count += 1
        else:
            # 抽象構文木をたどって関数名を取ってくる
            name = proto_node.function_declarator.identifier.identifier

            kind = "proto"
            return_type = proto_node.type_specifier.type_specifier

            objtype = ["fun", return_type]
            # 引数タイプを検査して追加
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
                "Line {0}: Function definition is available only at top-level.".format(funcdef_node.function_declarator.identifier.lineno))
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
        """抽象構文木のノードを受け取り、主に名前解析を行う(式の形の検査も含む)"""
        if isinstance(nodelist, ast.ExternalDeclarationList):
            for node in nodelist.nodes:
                print("Analyzing external declaration list...")
                print(node)
                print(node.__dict__)
                self.analyze(node, level)

        # 変数宣言の解析
        elif isinstance(nodelist, ast.Declaration):
            for declarator in nodelist.declarator_list.nodes:
                decl_decl = self.analyze_declaration(
                        nodelist, declarator, level)

                if isinstance(declarator.direct_declarator.identifier.identifier, Decl):
                    declname = declarator.direct_declarator.identifier.identifier.name
                    # break
                elif isinstance(declarator.direct_declarator.identifier.identifier, str):
                    declname = declarator.direct_declarator.identifier.identifier

                if self.env.lookup(declname, scope_index) is None:
                    self.env.add(decl_decl)
                    declarator.direct_declarator.identifier.identifier = decl_decl
                else:
                    existing_decl = self.env.lookup(
                        declname, scope_index)

                    # if existing_decl.level > level:
                        # scope_i = self.env.index(existing_decl)
                        # self.analyze(nodelist, level, scope_i+1)

                    declarator.direct_declarator.identifier.identifier = decl_decl

                    if existing_decl.kind == "fun" or existing_decl.kind == "proto":
                        if level == 0:
                            logging.error("Line {0}: {1} is defined as a function.".format(
                                declarator.direct_declarator.identifier.lineno, decl_decl.name))
                            self.error_count += 1
                        else:
                            self.env.add(decl_decl)
                            # declarator.direct_declarator.identifier.identifier = decl_decl

                    elif existing_decl.kind == "var":
                        if existing_decl.level == level:
                            logging.error("Line {0}: Duplicate declaration of variable - \"{1}\"".format(
                                declarator.direct_declarator.identifier.lineno, decl_decl.name))
                            self.error_count += 1
                        else:
                            self.env.add(decl_decl)
                            # declarator.direct_declarator.identifier.identifier = decl_decl

                    elif existing_decl.kind == "param":
                        self.env.add(decl_decl)
                        logging.warning("Line {0}: Variable declaration \"{1}\" will hide parameter \"{2}\".".format(
                            declarator.direct_declarator.identifier.lineno, funcdef_node.function_declarator.direct_declarator.identifier.identifier, existing_decl.name))
                        self.warning_count += 1

        # プロトタイプ宣言の解析
        elif isinstance(nodelist, ast.FunctionPrototype):
            decl_proto = self.analyze_func_prototype(nodelist, level)
            if self.env.lookup(decl_proto.name) is None:
                self.env.add(decl_proto)
                nodelist.function_declarator.identifier.identifier = decl_proto
            else:
                existing_decl = self.env.lookup(decl_proto.name)

                if existing_decl.kind == "fun":
                    if existing_decl.objtype != decl_proto.objtype:
                        logging.error("Line {0}: Type \"{1}\" of prototype definition \"{2}\" is conflicting with type \"{3}\" of function \"{4}\".".format(
                            nodelist.function_declarator.identifier.lineno, decl_proto.type, nodelist.function_declarator.identifier.identifier, existing_decl.type, existing_decl.name))
                        self.error_count += 1
                    else:
                        self.env.add(decl_proto)
                        nodelist.function_declarator.identifier.identifier = decl_proto
                elif existing_decl.kind == "proto":
                    if existing_decl.objtype[1] != decl_proto.objtype[1]:
                        logging.error("Line {0}: Type inconsintency of same named prototype definition {1}.".format(
                            nodelist.function_declarator.identifier.lineno, decl_proto.name))
                        self.error_count += 1
                    else:
                        self.env.add(decl_proto)
                        nodelist.function_declarator.identifier.identifier = decl_proto
                elif existing_decl.kind == "var":
                    if existing_decl.level == 0:
                        logging.error("Line {0}: Duplicate prototype declaration \"{1}\" with global variable \"{2}\"".format(
                            nodelist.function_declarator.identifier.lineno, nodelist.function_declarator.identifier.identifier, decl_proto.name))
                        self.error_count += 1
                    else:
                        self.env.add(decl_proto)
                        nodelist.function_declarator.identifier.identifier = decl_proto

            # self.analyze(
                # nodelist.function_declarator.parameter_type_list, level+1)

            param_list = []

            for paramdec in nodelist.function_declarator.parameter_type_list.nodes:
                decl_param = self.analyze_param_declaration(paramdec, level)

                # 重複チェック
                for existing_param in param_list:
                    if decl_param.name == existing_param.name:
                        logging.error("Line {0}: Parameter declaration \"{1}\" in function prototype declaration \"{2}\" is duplicated.".format(
                            paramdec.parameter_declarator.identifier.lineno, decl_param.name, existing_param.name))
                        self.error_count += 1
                param_list.append(decl_param)
                paramdec.parameter_declarator.identifier.identifier = decl_param

        elif isinstance(nodelist, ast.FunctionDefinition):
            decl_funcdef = self.analyze_func_definition(nodelist, level)

            if self.env.lookup(nodelist.function_declarator.identifier.identifier) is None:
                self.env.add(decl_funcdef)
                nodelist.function_declarator.identifier.identifier = decl_funcdef
            else:
                existing_decl = self.env.lookup(decl_funcdef.name)

                if existing_decl.kind == "fun":
                    logging.error("Line {0}: Function definition \"{1}\" is duplicated with existing function \"{2}\".".format(
                        nodelist.function_declarator.identifier.lineno, nodelist.function_declarator.identifier.identifier, existing_decl.name))
                    self.error_count += 1

                elif existing_decl.kind == "proto":
                    if existing_decl.objtype != decl_funcdef.objtype:
                        logging.error("Line {0}: Type of function prototype \"{1}\" is \"{2}\" , but type of function definition \"{3}\" is \"{4}\"".format(
                            nodelist.function_declarator.identifier.lineno, nodelist.function_declarator.identifier.identifier, decl_funcdef.objtype, existing_decl.name, existing_decl.objtype))
                        self.error_count += 1
                    else:
                        self.env.add(decl_funcdef)
                        nodelist.function_declarator.identifier.identifier = decl_funcdef

                elif existing_decl.kind == "var":
                    if existing_decl.level == 0:
                        logging.error("Line {0}: Function definition \"{1}\" is duplicated with global variable \"{2}\".".format(
                            nodelist.function_declarator.identifier.lineno, nodelist.function_declarator.identifier.identifier, existing_decl.name))
                        self.error_count += 1
                    else:
                        self.env.add(decl_funcdef)
                        nodelist.function_declarator.identifier.identifier = decl_funcdef

            try:
                func_index = self.env.decl_list.index(decl_funcdef)
                self.analyze(
                    nodelist.function_declarator.parameter_type_list, level+1)
                # self.analyze(nodelist.compound_statement, level+1)
                self.analyze(nodelist.compound_statement.declaration_list, level+2)
                self.analyze(nodelist.compound_statement.statement_list, level+2)
            except ValueError:
                sys.exit("Failed to get index of function {0} in environment.\n".format(
                    decl_funcdef.name))

        # 関数定義内のパラメータ解析
        elif isinstance(nodelist, ast.ParameterTypeList):
            param_list = []

            for paramdec in nodelist.nodes:
                decl_param = self.analyze_param_declaration(paramdec, level)

                # 重複チェック
                for param_into_env in param_list:
                    if decl_param.name == param_into_env.name:
                        logging.error("Line {0}: Parameter declaration \"{1}\" is duplicated with other parameter \"{2}\".".format(
                            paramdec.parameter_declarator.identifier.lineno, decl_param.name, param_into_env.name))
                        self.error_count += 1
                param_list.append(decl_param)
                paramdec.parameter_declarator.identifier.identifier = decl_param

            # 重複のなかったパラメータ宣言を環境に登録
            for param in param_list:
                self.env.add(param)

            # 何者？
            # for paramdec in nodelist.nodes:
            #     self.analyze(paramdec.parameter_declarator.identifier, level)

        elif isinstance(nodelist, ast.CompoundStatement):
            comp_level = level + 1
            for declaration in nodelist.declaration_list.nodes:
                self.analyze(declaration, level+1, scope_index)

            for statement in nodelist.statement_list.nodes:
                self.analyze(statement, level+1, scope_index)

            # 後始末
            for i, envelem in enumerate(self.env.decl_list):
                if envelem.level == comp_level:
                    self.env.deleted.append(self.env.decl_list.pop(i))

        elif isinstance(nodelist, ast.DeclarationList):
            for declaration in nodelist.nodes:
                self.analyze(declaration, level, scope_index)

        elif isinstance(nodelist, ast.StatementList):
            for statement in nodelist.nodes:
                self.analyze(statement, level, scope_index)

        elif isinstance(nodelist, ast.ExpressionStatement):
            self.analyze(nodelist.expression, level, scope_index)

        elif isinstance(nodelist, ast.FunctionExpression):
            # print("analyzing function expression nowwwwwwwwwww")
            # print(nodelist.__dict__)
            # print(nodelist.identifier.__dict__)
            # 関数名解析
            if self.env.lookup(nodelist.identifier.identifier) is None:
                logging.error("Line {0}: Referencing undeclared function \"{1}\".".format(
                    nodelist.identifier.lineno, nodelist.identifier.identifier))
                self.error_count += 1
            else:
                existing_decl = self.env.lookup(
                    nodelist.identifier.identifier)
                if existing_decl.kind == "fun" or existing_decl.kind == "proto":
                    nodelist.identifier.identifier = existing_decl
                elif existing_decl.kind == "proto" and existing_decl.name == "print":
                    print("found print expression!")
                    nodelist.identifier.identifier = existing_decl
                    print(nodelist.__dict__)
                    print(nodelist.identifier.identifier)
                elif existing_decl.kind == "var" or existing_decl.kind == "param":
                    logging.error("Line {0}: Referencing variable {1} as a function.".format(
                        nodelist.identifier.lineno, nodelist.identifier.identifier))
                    self.error_count += 1

            # パラメータ解析
            self.analyze(nodelist.argument_expression)

        elif isinstance(nodelist, ast.ArgumentExpressionList):
            for argnode in nodelist.nodes:
                self.analyze(argnode, level, scope_index)

        elif isinstance(nodelist, ast.BinaryOperators):
            self.analyze(nodelist.left, level, scope_index)
            self.analyze(nodelist.right, level, scope_index)

            # 式の形の検査
            if isinstance(nodelist.left, ast.Identifier):
                binop_left = self.env.lookup(nodelist.left.identifier.name)

                if nodelist.op == "ASSIGN":
                    if binop_left.kind == "fun" or binop_left.kind == "proto":
                        logging.error("Line {0}: Left-hand side of assignment should be variable, but \"{1}\" is a {2}.".format(
                            nodelist.left.lineno, binop_left.name, binop_left.kind))
                        self.error_count += 1
                    elif isinstance(binop_left.objtype, tuple) and binop_left.objtype[0] == "array":
                        logging.error("Line {0}: Variable at left-hand side of assignment must not be array type - about variable \"{1}\".".format(
                            nodelist.left.lineno, binop_left.name))
                        self.error_count += 1

        elif isinstance(nodelist, ast.Address):
            self.analyze(nodelist.expression, level, scope_index)

            # 式の形の検査
            if isinstance(nodelist.expression.identifier, str):
                exp = self.env.lookup(
                    nodelist.expression.identifier)
            elif isinstance(nodelist.expression.identifier, Decl):
                exp = self.env.lookup(
                    nodelist.expression.identifier.name)

            if exp is None:
                logging.error("Line {0}: Referencing undeclared variable \"{1}\".".format(
                    nodelist.expression.identifier.lineno, nodelist.expression.identifier.identifier))
            elif exp.kind != "var":
                logging.error("Line {0}: Illegal operand type \"{1}\" of pointer expression.".format(
                    nodelist.expression.identifier.lineno, exp.name))
                self.error_count += 1

        elif isinstance(nodelist, ast.Pointer):
            self.analyze(nodelist.expression, level, scope_index)

        elif isinstance(nodelist, ast.Identifier):
            if isinstance(nodelist.identifier, str):
                id_name = nodelist.identifier
            elif isinstance(nodelist.identifier, Decl):
                id_name = nodelist.identifier.name

            if self.env.lookup(id_name) is None:
                logging.error("Line {0}: Referencing undeclared variable \"{0}\".".format(
                    nodelist.lineno, id_name))
                self.error_count += 1
            else:
                existing_decl = self.env.lookup(id_name)

                if existing_decl.kind == "fun":
                    logging.error("Line {0}: Referencing function \"{1}\" as a variable.".format(
                        nodelist.lineno, existing_decl.name))
                    self.error_count += 1
                elif existing_decl.kind == "var" or existing_decl.kind == "param":
                    if isinstance(nodelist.identifier, str):
                        nodelist.identifier = existing_decl

        elif isinstance(nodelist, ast.IfStatement):
            print("analyzer if statement")
            print("then: {0}".format(nodelist.then_statement))
            print("else: {0}".format(nodelist.else_statement))
            self.analyze(nodelist.expression, level+1, scope_index)
            self.analyze(nodelist.then_statement, level+1, scope_index)
            self.analyze(nodelist.else_statement, level+1, scope_index)

        elif isinstance(nodelist, ast.WhileLoop):
            self.analyze(nodelist.expression, level+1, scope_index)
            self.analyze(nodelist.statement, level+1, scope_index)

        elif isinstance(nodelist, ast.ForLoop):
            self.analyze(nodelist.firstexp_statement, level, scope_index)
            self.analyze(nodelist.whileloop_node, level, scope_index)

        elif isinstance(nodelist, ast.ReturnStatement):
            self.analyze(nodelist.return_statement, level, scope_index)

        return self.env, self.env.deleted


class TypeChecker(object):
    """型検査のための関数をまとめたクラス"""
    def __init__(self, env):
        self.env = env

    # 型検査の本体関数
    def check_type(self, nodelist):
        if isinstance(nodelist, ast.NullNode):
            pass

        # top level
        elif isinstance(nodelist, ast.ExternalDeclarationList):
            for node in nodelist.nodes:
                self.check_type(node)

        # declaration
        elif isinstance(nodelist, ast.Declaration):
            self.check_type(nodelist.declarator_list)

        elif isinstance(nodelist, ast.DeclaratorList):
            for declarator in nodelist.nodes:
                self.check_type(declarator)

        elif isinstance(nodelist, ast.Declarator):
            self.check_type(nodelist.direct_declarator)

        elif isinstance(nodelist, ast.DirectDeclarator):
            pass

        elif isinstance(nodelist, ast.FunctionPrototype):
            pass

        elif isinstance(nodelist, ast.FunctionDefinition):
            # 返り値の型の整合性チェック
            return_exists, func_return = self.check_return(nodelist.compound_statement)
            if return_exists: # returnがあれば型チェックが発生
                if not nodelist.type_specifier.type_specifier == "void" and func_return == "void":
                    logging.error("Line {0}: Function \"{1}\" returns void, but defined as {2} type.".format(
                        nodelist.function_declarator.identifier.lineno, nodelist.function_declarator.identifier.identifier.name, nodelist.type_specifier.type_specifier))
                    self.error_count += 1

                elif nodelist.type_specifier.type_specifier == "void" and not func_return == "void":
                        logging.error("Line {0}: Function \"{1}\" returns {2}, but defined as void type.".format(
                            nodelist.function_declarator.identifier.lineno, nodelist.function_declarator.identifier.identifier.name, func_return))
                        self.error_count += 1

            # 関数定義内の複文の型チェック
            self.check_type(nodelist.compound_statement)

        elif isinstance(nodelist, ast.CompoundStatement):
            self.check_type(nodelist.declaration_list)
            self.check_type(nodelist.statement_list)

        elif isinstance(nodelist, ast.DeclarationList):
            for node in nodelist.nodes:
                self.check_type(node)

        elif isinstance(nodelist, ast.StatementList):
            for node in nodelist.nodes:
                self.check_type(node)

        elif isinstance(nodelist, ast.ExpressionStatement):
            self.check_type(nodelist.expression)

        elif isinstance(nodelist, ast.IfStatement):
            if not self.check_type(nodelist.expression) == "int":
                logging.error(
                    "Line {0}: Expression of if statement must return int-type.".format(nodelist.lineno))
                self.error_count += 1
            self.check_type(nodelist.then_statement)
            self.check_type(nodelist.else_statement)

        elif isinstance(nodelist, ast.WhileLoop):
            if not self.check_type(nodelist.expression) == "int":
                logging.error(
                    "Line {0}: Expression of while statement must return int-type.".format(nodelist.lineno))
                self.error_count += 1
            self.check_type(nodelist.statement)

        elif isinstance(nodelist, ast.ReturnStatement):
            # print(type(nodelist.return_statement))
            self.check_type(nodelist.return_statement)

        elif isinstance(nodelist, ast.BinaryOperators):
            if nodelist.op == "ASSIGN":
                if self.check_type(nodelist.left) == self.check_type(nodelist.right):
                    return self.check_type(nodelist.left)
                else:
                    logging.error(
                        "Line {0}: Type inconsintency between left-hand {1} and right-hand {2} of assign expression.".format(nodelist.lineno, nodelist.left, nodelist.right))
                    self.error_count += 1

            elif nodelist.op == "AND" or nodelist.op == "OR":
                if self.check_type(nodelist.left) == "int" and self.check_type(nodelist.right) == "int":
                    return "int"
                else:
                    logging.error("Line {0}: Type inconsisntency of logical expression.".format(nodelist.lineno))
                    # print("Type of logical left: {0}".format(
                    #     self.check_type(nodelist.left)))
                    # print("Type of logical right: {0}".format(
                    #     self.check_type(nodelist.right)))
                    self.error_count += 1

            elif nodelist.op == "EQUAL" \
                    or nodelist.op == "NEQ" \
                    or nodelist.op == "LT" \
                    or nodelist.op == "GT" \
                    or nodelist.op == "LEQ" \
                    or nodelist.op == "GEQ":
                if self.check_type(nodelist.left) == self.check_type(nodelist.right):
                    return "int"
                else:
                    logging.error(
                        "Line {0}: Type inconsintency between left-hand {1} and right-hand {2} of relational expression.".format(nodelist.lineno, nodelist.left, nodelist.right))
                    # print("Type of relational left: {0}".format(
                    #     self.check_type(nodelist.left)))
                    # print("Type of relational right: {0}".format(
                    #     self.check_type(nodelist.right)))
                    self.error_count += 1

            elif nodelist.op == "PLUS" \
                    or nodelist.op == "TIMES" \
                    or nodelist.op == "DIVIDE":
                if self.check_type(nodelist.left) == self.check_type(nodelist.right) == "int":
                    return "int"
                elif self.check_type(nodelist.left) == "int" and self.check_type(nodelist.right) == ("pointer", "int"):
                    # nodelist.left = ast.BinaryOperators(
                        # "TIMES", nodelist.left, ast.Number(4))
                    return ("pointer", "int")
                elif self.check_type(nodelist.left) == ("pointer", "int") and self.check_type(nodelist.right) == "int":
                    # nodelist.right = ast.BinaryOperators(
                        # "TIMES", nodelist.right, ast.Number(4), nodelist.left.lineno)
                    return ("pointer", "int")
                else:
                    logging.error(
                        "Line {0}: Type inconsintency between left-hand and right-hand of calculation.".format(nodelist.lineno))
                    self.error_count += 1

            elif nodelist.op == "MINUS":
                if self.check_type(nodelist.left) == self.check_type(nodelist.right) == "int":
                    return "int"
                elif self.check_type(nodelist.left) == ("pointer", "int") and self.check_type(nodelist.right) == "int":
                    nodelist.right = ast.BinaryOperators(
                        "TIMES", nodelist.right, ast.Number(4))
                    return ("pointer", "int")
                else:
                    logging.error(
                        "Line {0}: Type inconsintency between left-hand and right-hand of calculation.".format(nodelist.lineno))
                    self.error_count += 1

        elif isinstance(nodelist, ast.Address):
            if self.check_type(nodelist.expression) == "int":
                return ("pointer", "int")
            else:
                logging.error(
                    "Line {0}: Invalid type for operand of pointer expression.".format(nodelist.lineno))
                self.error_count += 1

        elif isinstance(nodelist, ast.Pointer):
            if self.check_type(nodelist.expression) == ("pointer", "int"):
                return "int"
            else:
                logging.error("Line {0}: Invalid operand of *( ), not a pointer type.".format(nodelist.lineno))
                self.error_count += 1

        elif isinstance(nodelist, ast.FunctionExpression):
            if isinstance(nodelist.identifier.identifier, str):
                funcname = nodelist.identifier.identifier
            elif isinstance(nodelist.identifier.identifier, Decl):
                funcname = nodelist.identifier.identifier.name

            func_decl = self.env.lookup(funcname)
            # 引数の個数チェック
            if isinstance(nodelist.argument_expression, ast.NullNode):
                arglen = 0
            else:
                arglen = len(nodelist.argument_expression.nodes)
                if arglen > len(func_decl.objtype[2:]):
                    logging.error("Line {0}: Too many arguments for function {1}.".format(
                        nodelist.lineno, func_decl.name))
                    self.error_count += 1
                elif arglen < len(func_decl.objtype[2:]):
                    logging.error("Line {0}: Too few arguments for function {0}.".format(
                        nodelist.lineno, func_decl.name))
                    self.error_count += 1
                else:  # 引数の個数が一致したとき
                    # 引数の型チェック
                    # if arglen == 0:
                        # return func_decl.objtype[1]
                    # else:
                    for i, argnode in enumerate(nodelist.argument_expression.nodes):
                        if not self.check_type(argnode) == func_decl.objtype[2+i]:
                            ill_type = self.check_type(argnode)
                            logging.error("Line {0}: Taking {1} type argument for function {2} - correct type is {2}.".format(
                                nodelist.lineno, ill_type, func_decl.name. func_decl.objtype[2+i]))
                            self.error_count += 1

                    # print("Type checking of function expression and returning {0}...".format(
                    #     func_decl.objtype[1]))
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

        # return self.error_count, self.warning_count

    # 関数の返り値の型を返す関数
    def check_return(self, stmtnode):
        return_exists = False
        return_strtype = "void"
        if isinstance(stmtnode, ast.ReturnStatement):
            return_exists = True
            if not isinstance(stmtnode.return_statement, ast.NullNode):
                # voidじゃない
                return_strtype = self.check_type(stmtnode.return_statement)

        elif isinstance(stmtnode, ast.CompoundStatement):
            for stmt in stmtnode.statement_list.nodes:
                self.check_return(stmt)

        elif isinstance(stmtnode, ast.IfStatement):
            self.check_return(stmtnode.then_statement)
            self.check_return(stmtnode.else_statement)

        elif isinstance(stmtnode, ast.WhileLoop):
            self.check_return(stmtnode.statement)

        elif isinstance(stmtnode, ast.StatementList):
            for stmt in stmtnode.nodes:
                self.check_return(stmt)

        return return_exists, return_strtype


class ErrorManager(object):

    def __init__(self, e_cnt, w_cnt):
        # self.error_msg = e_msg
        # self.warning_msg = w_msg
        self.error_count = e_cnt
        self.warning_count = w_cnt

    def print_error(self):
        print("{0} Errors and {1} Warnings.".format(
            self.error_count, self.warning_count))

        # if not logging.warning == "":
        #     sys.stderr.write(logging.warning)

        # if not self.error_msg == "":
        #     sys.exit(logging.error)
