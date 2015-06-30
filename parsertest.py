#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
# from parser import Parser

testcode1 = """
int func(int a, int b) {
    int i;
    i = 0;
    for (;;) {
        if (i == a) {
            break;
        } else {
            i++;
        }
    }

    for ( ; i > b; i--) {
        print(i);
    }

    return i;
}
"""

testcode2 = """
void func(int a, int b) {
    int i;
    i = 0;
    while (i < a) {
        i += b;

    }

}

"""

testcode3 = """
void bubble_sort(int *data) {\n
    int i, j, tmp;\n
    for (i = 0; i < AMOUNT - 1; i++) {\n
        for (j = AMOUNT - 1; j > i; j--) {\n
            if (data[j-1] > data[j]) {\n
                tmp = data[j];\n
                data[j] = data[j-1];\n
                data[j-1] = tmp;\n
            }\n
        }\n
    }\n
}\n

int main() {\n
    int i;\n
\n
    /* initialize */\n
    data[0] = 3;\n
    data[1] = 5;\n
    data[2] = 10;\n
    data[3] = 7;\n
    data[4] = 1;\n
    data[5] = 4;\n
    data[6] = 12;\n
    data[7] = 6;\n
\n
    /* sort */\n
    bubble_sort(data);\n
\n
    /* print */\n
    for (i = 0; i < AMOUNT; i++) {\n
        print(&data[i]);\n
    }\n
\n
    return 0;\n
}\n

"""

# include syntax error
testcode4 = """
int func_error(int n) {
    int i;
    while (i < n) {
        i++
    }
    return i;
}
"""

testcode5 = """
int main (int a) {
    int i;
    i = -a;
    return i;
}
"""

testcode6 = """
int i;
int j;
int *k;
int array[8];
int *p_array[5];

int func1(int a, int b);
void func2();
int func1(int i); /* duplicate but type consistent prototype */
void func1(); /* duplicate and type inconsistent prototype */
int func3(int a, int *array);
void func4(int a, int a); /* duplicate param declaration */

int main() {
    int i;
    i = 0;
    return i;
}

/* duplicate function definition */
int main(int i) {
    return i;
}

/* duplicate with variable declaration */
void i() {
    ;
}

/* illegal operand of pointer */
void func() {
    func1(&func2);
}
"""

# 式検査の動作チェック用コード
testcode7 = """
int global;
int inc(int a);
void func_stmtcheck();
int return_void(int a);
void return_int(int a);

int inc(int a) {
    return a+1;
}

void func_stmtcheck() {
    int array[5];
    int i;
    void j;

    array = 0;
    inc = 1;
    i = &inc;
}

int return_void(int r) {
    int tmp;
    tmp = r;
}

void return_int(int v) {
    return v;
}
"""