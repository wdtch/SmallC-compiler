# import unittest
from parser import Parser

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
void bubble_sort(int *data) {
    int i, j, tmp;
    for (i = 0; i < AMOUNT - 1; i++) {
        for (j = AMOUNT - 1; j > i; j--) {
            if (data[j-1] > data[j]) {
                tmp = data[j];
                data[j] = data[j-1];
                data[j-1] = tmp;
            }
        }
    }
}

int main() {
    int i;

    /* initialize */
    data[0] = 3;
    data[1] = 5;
    data[2] = 10;
    data[3] = 7;
    data[4] = 1;
    data[5] = 4;
    data[6] = 12;
    data[7] = 6;

    /* sort */
    bubble_sort(data);

    /* print */
    for (i = 0; i < AMOUNT; i++) {
        print(&data[i]);
    }

    return 0;
}

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
"""