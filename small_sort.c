#include <stdio.h>

/* #define AMOUNT 8 */


void bubble_sort(int *data);
void output(int *data);
void print(int *v);

int data[8];

void bubble_sort(int *data) {
    int i, j, tmp;
    for (i = 0; i < 8 - 1; i++) {
        for (j = 8 - 1; j > i; j--) {
            if (data[j-1] > data[j]) {
                tmp = data[j];
                data[j] = data[j-1];
                data[j-1] = tmp;
            }
        }
    }
}

void output(int *data) {
    int i;
    i = 0;
    while (i < 8) {
        print(&data[i]);
        i++;
    }
}

void print(int *v) {
    printf("%d ", *v);
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
    for (i = 0; i < 8; i++) {
        print(&data[i]);
    }

    return 0;
}
