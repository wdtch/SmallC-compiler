#!/usr/bin/python
# -*- coding: utf-8 -*-

"""構文解析モジュール"""

from __future__ import unicode_literals, print_function
import ply.lex as lex
import ply.yacc as yacc
import tokenrules
from lexer import Lexer
import ast
import restorecode
import parsertest
import semantic_analyzer


class Parser(object):
    tokens = tokenrules.tokens

    # program
    def p_program_ex(self, p):
        '''program : external-declaration'''
        p[0] = ast.ExternalDeclarationList(p[1])

    def p_program_prog(self, p):
        '''program : program external-declaration'''
        p[1].append(p[2])
        p[0] = p[1]


    # declaration
    def p_external_declaration(self, p):
        '''external-declaration : declaration
                                | function-prototype
                                | function-definition'''
        p[0] = p[1]

    def p_declaration(self, p):
        '''declaration : type-specifier declarator-list SEMICOLON'''
        p[0] = ast.Declaration(p[1], p[2])


    # declarator
    def p_declarator_list(self, p):
        '''declarator-list : declarator'''
        p[0] = ast.DeclaratorList(p[1])

    def p_declarator_list_list(self, p):
        '''declarator-list : declarator-list COMMA declarator'''
        p[1].append(p[3])
        p[0] = p[1]

    def p_declarator(self, p):
        '''declarator : direct-declarator'''
        p[0] = ast.Declarator("NORMAL", p[1])

    def p_declarator_val(self, p):
        '''declarator : TIMES direct-declarator'''
        p[0] = ast.Declarator("POINTER", p[2])

    def p_direct_declarator(self, p):
        '''direct-declarator : identifier'''
        p[0] = ast.DirectDeclarator(p[1])

    def p_direct_declarator_array(self, p):
        '''direct-declarator : identifier LBRACKET constant RBRACKET'''
        p[0] = ast.DirectArrayDeclarator(p[1], p[3])


    # function
    def p_function_prototype(self, p):
        '''function-prototype : type-specifier function-declarator SEMICOLON'''
        p[0] = ast.FunctionPrototype(p[1], p[2])

    def p_function_declarator(self, p):
        '''function-declarator : identifier LPAREN parameter-type-list RPAREN'''
        p[0] = ast.FunctionDeclarator("NORMAL", p[1], p[3])

    def p_function_declarator_noparam(self, p):
        '''function-declarator : identifier LPAREN RPAREN'''
        p[0] = ast.FunctionDeclarator("NORMAL", p[1], ast.NullNode())

    def p_function_declarator_pointer(self, p):
        '''function-declarator : TIMES identifier LPAREN parameter-type-list RPAREN'''
        p[0] = ast.FunctionDeclarator("POINTER", p[2], p[4])

    def p_function_declarator_pointer_noparam(self, p):
        '''function-declarator : TIMES identifier LPAREN RPAREN'''
        p[0] = ast.FunctionDeclarator("POINTER", p[2], ast.NullNode())

    def p_fuction_definition(self, p):
        '''function-definition : type-specifier function-declarator compound-statement'''
        p[0] = ast.FunctionDefinition(p[1], p[2], p[3])


    # parameter
    def p_parameter_type_list_declaration(self, p):
        '''parameter-type-list : parameter-declaration'''
        p[0] = ast.ParameterTypeList(p[1])

    def p_parameter_type_list_list(self, p):
        '''parameter-type-list : parameter-type-list COMMA parameter-declaration'''
        p[1].append(p[3])
        p[0] = p[1]

    def p_parameter_declaration(self, p):
        '''parameter-declaration : type-specifier parameter-declarator'''
        p[0] = ast.ParameterDeclaration(p[1], p[2])

    def p_parameter_declarator(self, p):
        '''parameter-declarator : identifier'''
        p[0] = ast.ParameterDeclarator("NORMAL", p[1])

    def p_paramenter_declarator_pointer(self, p):
        '''parameter-declarator : TIMES identifier'''
        p[0] = ast.ParameterDeclarator("POINTER", p[2])


    # type specifier
    def p_type_specifier(self, p):
        '''type-specifier : INT
                          | VOID'''
        p[0] = ast.TypeSpecifier(p[1])


    # statement
    def p_statement_semicolon(self, p):
        '''statement : SEMICOLON'''
        p[0] = ast.NullNode()

    def p_statement_expression(self, p):
        '''statement : expression SEMICOLON'''
        p[0] = ast.ExpressionStatement(p[1])

    def p_statement_compound_statement(self, p):
        '''statement : compound-statement'''
        p[0] = p[1]


    # if statement
    def p_statement_if(self, p):
        '''statement : IF LPAREN expression RPAREN statement'''
        p[0] = ast.IfStatement(p[3], p[5], ast.NullNode())

    def p_statement_if_else(self, p):
        '''statement : IF LPAREN expression RPAREN statement ELSE statement'''
        p[0] = ast.IfStatement(p[3], p[5], p[7])

    # while loop
    def p_statement_while(self, p):
        '''statement : WHILE LPAREN expression RPAREN statement'''
        p[0] = ast.WhileLoop(p[3], p[5])

    # for loop
    def p_statement_for(self, p):
        '''statement : FOR LPAREN expression SEMICOLON expression SEMICOLON expression RPAREN statement'''
        p[9].statement_list.append(ast.ExpressionStatement(p[7]))
        p[0] = ast.ForLoop(ast.ExpressionStatement(p[3]), ast.WhileLoop(p[5], p[9]))

    def p_statement_for_noinit(self, p):
        '''statement : FOR LPAREN SEMICOLON expression SEMICOLON expression RPAREN statement'''
        p[8].statement_list.append(ast.ExpressionStatement(p[6]))
        p[0] = ast.ForLoop(ast.NullNode(), ast.WhileLoop(p[4], p[8]))

    def p_statement_for_noend(self, p):
        '''statement : FOR LPAREN expression SEMICOLON SEMICOLON expression RPAREN statement'''
        p[8].statement_list.append(ast.ExpressionStatement(p[6]))
        p[0] = ast.ForLoop(ast.ExpressionStatement(p[3]), ast.WhileLoop(ast.Number(1), p[8]))

    def p_statement_for_novar(self, p):
        '''statement : FOR LPAREN expression SEMICOLON expression SEMICOLON RPAREN statement'''
        p[0] = ast.ForLoop(ast.ExpressionStatement(p[3]), ast.WhileLoop(p[5], p[8]))

    def p_statement_for_onlyinit(self, p):
        '''statement : FOR LPAREN expression SEMICOLON SEMICOLON RPAREN statement'''
        p[0] = ast.ForLoop(ast.ExpressionStatement(p[3]), ast.WhileLoop(ast.Number(1), p[7]))

    def p_statement_for_onlyend(self, p):
        '''statement : FOR LPAREN SEMICOLON expression SEMICOLON RPAREN statement'''
        p[0] = ast.ForLoop(ast.NullNode(), ast.WhileLoop(p[4], p[7]))

    def p_statement_for_onlyvar(self, p):
        '''statement : FOR LPAREN SEMICOLON SEMICOLON expression RPAREN statement'''
        p[7].statement_list.append(ast.ExpressionStatement(p[5]))
        p[0] = ast.ForLoop(ast.NullNode(), ast.WhileLoop(ast.Number(1), p[7]))

    def p_statement_for_noexp(self, p):
        '''statement : FOR LPAREN SEMICOLON SEMICOLON RPAREN statement'''
        p[0] = ast.ForLoop(ast.NullNode(), ast.WhileLoop(ast.Number(1), p[6]))


    # return statement
    def p_statement_return_void(self, p):
        '''statement : RETURN SEMICOLON'''
        p[0] = ast.ReturnStatement(ast.NullNode())

    def p_statement_return(self, p):
        '''statement : RETURN expression SEMICOLON'''
        p[0] = ast.ReturnStatement(p[2])


    # compound statement
    def p_compound_statement_empty(self, p):
        '''compound-statement : LBRACE RBRACE'''
        p[0] = ast.CompoundStatement(ast.NullNode(), ast.NullNode())

    def p_compound_statement_declaration(self, p):
        '''compound-statement : LBRACE declaration-list RBRACE'''
        p[0] = ast.CompoundStatement(ast.DeclaratorList(p[2]), ast.StatementList(ast.NullNode()))

    def p_compound_statement_statement(self, p):
        '''compound-statement : LBRACE statement-list RBRACE'''
        p[0] = ast.CompoundStatement(ast.DeclarationList(ast.NullNode()), ast.StatementList(p[2]))

    def p_compound_statement_declaration_statement(self, p):
        '''compound-statement : LBRACE declaration-list statement-list RBRACE'''
        p[0] = ast.CompoundStatement(ast.DeclaratorList(p[2]), ast.StatementList(p[3]))


    # declaration list
    def p_declaration_list(self, p):
        '''declaration-list : declaration'''
        p[0] = ast.DeclarationList(p[1])

    def p_declaration_list_declaration_list(self, p):
        '''declaration-list : declaration-list declaration'''
        p[1].append(p[2])
        p[0] = p[1]


    # statement list
    def p_statement_list(self, p):
        '''statement-list : statement'''
        p[0] = ast.StatementList(p[1])

    def p_statement_list_statement_list(self, p):
        '''statement-list : statement-list statement'''
        p[1].append(p[2])
        p[0] = p[1]


    # expression
    def p_expression_assign_expr(self, p):
        '''expression : assign-expr'''
        p[0] = p[1]

    def p_expression_expression(self, p):
        '''expression : expression COMMA assign-expr'''
        p[0] = p[1].append(p[3])


    # assign
    def p_assign_expr_or(self, p):
        '''assign-expr : logical-OR-expr'''
        p[0] = p[1]

    def p_assign_expr_assign(self, p):
        '''assign-expr : logical-OR-expr ASSIGN assign-expr'''
        p[0] = ast.BinaryOperators("ASSIGN", p[1], p[3])

    def p_plus_equal(self, p):
        '''assign-expr : logical-OR-expr PLUS_EQ assign-expr'''
        p[0] = ast.BinaryOperators("ASSIGN", p[1], ast.BinaryOperators("PLUS", p[1], p[3]))

    def p_minus_equal(self, p):
        '''assign-expr : logical-OR-expr MINUS_EQ assign-expr'''
        p[0] = ast.BinaryOperators("ASSIGN", p[1], ast.BinaryOperators("MINUS", p[1], p[3]))


    # logical expression
    def p_logical_OR_expr_and(self, p):
        '''logical-OR-expr : logical-AND-expr'''
        p[0] = p[1]

    def p_logical_OR_expr_or(self, p):
        '''logical-OR-expr : logical-OR-expr OR logical-AND-expr'''
        p[0] = ast.BinaryOperators("OR", p[1], p[3])

    def p_logical_AND_expr_equal(self, p):
        '''logical-AND-expr : equality-expr'''
        p[0] = p[1]

    def p_logical_AND_expr_and(self, p):
        '''logical-AND-expr : logical-AND-expr AND equality-expr'''
        p[0] = ast.BinaryOperators("AND", p[1], p[3])


    # relational operation
    def p_equality_expr_rel(self, p):
        '''equality-expr : relational-expr'''
        p[0] = p[1]

    def p_equality_expr_eq(self, p):
        '''equality-expr : equality-expr EQUAL relational-expr'''
        p[0] = ast.BinaryOperators("EQUAL", p[1], p[3])

    def p_equality_expr_neq(self, p):
        '''equality-expr : equality-expr NEQ relational-expr'''
        p[0] = ast.BinaryOperators("NEQ", p[1], p[3])

    def p_relational_expr_add(self, p):
        '''relational-expr : add-expr'''
        p[0] = p[1]

    def p_relational_expr_lt(self, p):
        '''relational-expr : relational-expr LT add-expr'''
        p[0] = ast.BinaryOperators("LT", p[1], p[3])

    def p_relational_expr_gt(self, p):
        '''relational-expr : relational-expr GT add-expr'''
        p[0] = ast.BinaryOperators("GT", p[1], p[3])

    def p_relational_expr_leq(self, p):
        '''relational-expr : relational-expr LEQ add-expr'''
        p[0] = ast.BinaryOperators("LEQ", p[1], p[3])

    def p_relational_expr_geq(self, p):
        '''relational-expr : relational-expr GEQ add-expr'''
        p[0] = ast.BinaryOperators("GEQ", p[1], p[3])


    # arithmetic operation
    def p_add_expr_mult(self, p):
        '''add-expr : mult-expr'''
        p[0] = p[1]

    def p_add_expr_plus(self, p):
        '''add-expr : add-expr PLUS mult-expr'''
        p[0] = ast.BinaryOperators("PLUS", p[1], p[3])

    def p_add_expr_minus(self, p):
        '''add-expr : add-expr MINUS mult-expr'''
        p[0] = ast.BinaryOperators("MINUS", p[1], p[3])

    def p_mult_expr_unary(self, p):
        '''mult-expr : unary-expr'''
        p[0] = p[1]

    def p_mult_expr_times(self, p):
        '''mult-expr : mult-expr TIMES unary-expr'''
        p[0] = ast.BinaryOperators("TIMES", p[1], p[3])

    def p_mult_expr_divide(self, p):
        '''mult-expr : mult-expr DIVIDE unary-expr'''
        p[0] = ast.BinaryOperators("DIV", p[1], p[3])


    # unary expression
    def p_unary_expr_post(self, p):
        '''unary-expr : postfix-expr'''
        p[0] = p[1]

    def p_unary_expr_minus(self, p):
        '''unary-expr : MINUS unary-expr'''
        # p[0] = ast.Negative(p[2])
        p[0] = ast.BinaryOperators("MINUS", ast.Number(0), p[2])

    def p_unary_expr_addr(self, p):
        '''unary-expr : ADDRESS unary-expr'''
        if isinstance(p[2], ast.Pointer):
            p[0] = p[2].expression
        else:
            p[0] = ast.Address(p[2])

    def p_unary_expr_val(self, p):
        '''unary-expr : TIMES unary-expr'''
        p[0] = ast.Pointer(p[2])

    def p_unary_expr_inc(self, p):
        '''unary-expr : identifier INC'''
        # p[0] = ast.Increment(p[1])
        p[0] = ast.BinaryOperators("ASSIGN", p[1], ast.BinaryOperators("PLUS", p[1], ast.Number(1)))

    def p_unary_expr_dec(self, p):
        '''unary-expr : identifier DEC'''
        # p[0] = ast.Decrement(p[1])
        p[0] = ast.BinaryOperators("ASSIGN", p[1], ast.BinaryOperators("MINUS", p[1], ast.Number(1)))


    # postfix expression
    def p_postfix_expr_primary(self, p):
        '''postfix-expr : primary-expr'''
        p[0] = p[1]

    def p_postfix_expr_array(self, p):
        '''postfix-expr : postfix-expr LBRACKET expression RBRACKET'''
        # p[0] = ast.ArrayExpression(p[1], p[3])
        p[0] = ast.Pointer(ast.BinaryOperators("PLUS", p[1], p[3]))

    def p_postfix_expr_nullarg(self, p):
        '''postfix-expr : identifier LPAREN RPAREN'''
        p[0] = ast.FunctionExpression(p[1], ast.NullNode(), p[1].lineno)

    def p_postfix_expr_arg(self, p):
        '''postfix-expr : identifier LPAREN argument-expression-list RPAREN'''
        p[0] = ast.FunctionExpression(p[1], p[3], p[1].lineno)


    # primary expression
    def p_primary_expr_id(self, p):
        '''primary-expr : identifier'''
        p[0] = p[1]

    def p_primary_expr_const(self, p):
        '''primary-expr : constant'''
        p[0] = p[1]

    def p_primary_expr_expr(self, p):
        '''primary-expr : LPAREN expression RPAREN'''
        p[0] = p[2]


    # argument expression
    def p_argument_expression_list_assign(self, p):
        '''argument-expression-list : assign-expr'''
        p[0] = ast.ArgumentExpressionList(p[1])

    def p_argument_expression_list_list(self, p):
        '''argument-expression-list : argument-expression-list COMMA assign-expr'''
        p[1].append(p[3])
        p[0] = p[1]


    # identifier
    def p_identifier(self, p):
        '''identifier : ID'''
        p[0] = ast.Identifier(p[1], p.lineno(1))


    # constant
    def p_constant(self, p):
        '''constant : NUMBER'''
        p[0] = ast.Number(p[1])


    # def p_empty(self, p):
    #     '''empty : '''
    #     p[0] = ast.NullNode()

    def p_error(self, p):
        if p:
            print("Syntax error at token", p.type)
            # Just discard the token and tell the parser it's okay.
            self.parser.errok()
        else:
            print("Syntax error at EOF")

    # 解析実行部
    def build(self, debug=False, **kwargs):
        # 字句解析
        self.lexer = Lexer()
        self.lexer.build(debug=debug)

        # 構文解析
        self.parser = yacc.yacc(module=self, debug=debug)

        # ここから単体テスト
        if __name__ == '__main__':
            print("choose test.")
            # select = raw_input()
            # selecting testcode6 for testing semantic analyzer
            select = "7"
            if select == "1":
                # testcode1をパース、復元
                print("Parse and restore code1.")
                try:
                    s = """void print(int i);""" + parsertest.testcode1
                except EOFError:
                    print("EOF Error!(;_;)")
                # パース
                result = self.parser.parse(s)
                # コード復元部
                restorecode.restore_code(result)
                print("")

            elif select == "2":
                # testcode2をパース、復元
                print("Parse and restore code2.")
                try:
                    s = """void print(int i);""" + parsertest.testcode2
                except EOFError:
                    print("EOF Error!(;_;)")
                # パース
                result = self.parser.parse(s)
                # コード復元部
                restorecode.restore_code(result)
                print("")

            elif select == "3":
                # testcode3をパース、復元
                print("Parse and restore code3.")
                try:
                    s = """void print(int i);\n""" + parsertest.testcode3
                except EOFError:
                    print("EOF Error!(;_;)")
                # パース
                result = self.parser.parse(s)
                # コード復元部
                restorecode.restore_code(result)
                print("")

            elif select == "4":
                # testcode4をパース、復元
                print("Parse and restore code4.")
                try:
                    s = """void print(int i);""" + parsertest.testcode4
                except EOFError:
                    print("EOF Error!(;_;)")
                # パース
                result = self.parser.parse(s)
                # コード復元部
                restorecode.restore_code(result)
                print("")

            elif select == "5":
                # testcode5をパース、復元
                print("Parse and restore code5.")
                try:
                    s = """void print(int i);""" + parsertest.testcode5
                except EOFError:
                    print("EOF Error!(;_;)")
                # パース
                result = self.parser.parse(s)
                # コード復元部
                restorecode.restore_code(result)
                print("")

            elif select == "6":
                # testcode6をパース、復元→意味解析へ
                print("Parse and restore code6.")
                try:
                    s = parsertest.testcode6
                except EOFError:
                    print("EOF Error!(;_;)")
                # パース
                result = self.parser.parse(s)
                # コード復元部
                restorecode.restore_code(result)
                print("")

            elif select == "7":
                # testcode6をパース、復元→意味解析へ
                print("Parse and restore code7.")
                try:
                    s = parsertest.testcode7
                except EOFError:
                    print("EOF Error!(;_;)")
                # パース
                result = self.parser.parse(s)
                # コード復元部
                restorecode.restore_code(result)
                print("")

            analyzer = semantic_analyzer.Analyzer(result)
            env = analyzer.analyze(analyzer.nodelist)
            e_msg, w_msg, e_cnt, w_cnt = analyzer.check_type(analyzer.nodelist, env)
            error_mng = semantic_analyzer.ErrorManager(e_msg, w_msg, e_cnt, w_cnt)
            error_mng.print_error()

myparser = Parser()
myparser.build()
