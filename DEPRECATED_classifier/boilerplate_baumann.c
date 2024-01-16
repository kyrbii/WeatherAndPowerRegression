#include <assert.h>
#include <stdio.h>
#include <stdlib.h> // exit
#include <string.h>
#include <stdbool.h>
#include <math.h>

typedef enum distance {MANHATTAN, EUCLIDEAN} distance;

/**
 * reads up to n items from a given file and fills them into x and y
 * @param n the (maximum) number of items to be read from CSV file
 * @param d the dimensionality of the items (plus one more for y)
 * @param x
 * @param y
 * @param filename
 * @return the number of items actually read (can be lower if CSV file is shorter)
 */
int read_csv(char* filename, int n, int d, double x[n][d], int y[d]) {
    FILE* f = fopen(filename, "r");
    if (f == NULL) {
        printf("%s cannot be found", filename);
        exit(2);
    } // let's now continue as if f is not NULL (otherwise we have already aborted)
    // discard the first line (let's hope that it's not longer than that)
    // BUG ALERT: do not write this in production code but find out how to safely read a full line.
    char line[65536];
    fgets(line, 65536, f);
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < d; j++) {
            int ret = fscanf(f, "%lf,", &x[i][j]);
            if (ret == EOF) {
                fclose(f);
                return i;
            }
        }
        int ret = fscanf(f, "%d", &y[i]);
        if (ret == EOF) {
            fclose(f);
            return i;
        }
    }
    fclose(f);
    return n;
}

void print_csv(int n, int d, double x[n][d], int y[n]) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < d; j++) {
            printf("%lf, ", x[i][j]);
        }
        printf("%d\n", y[i]);
    }
}

void copy_instance(int d, double src[d], double tgt[d]) {
    for (int i = 0; i < d; i++) {
        tgt[i] = src[i];
    }
}

void split_train_test(int test, int n, int d, double full_x[n][d], const int full_y[n], double train_x[n-1][d], int train_y[n-1], double test_x[d], int* test_y) {
    // these are identical until we hit the test item
    int i = 0; // index over full variables
    int j = 0; // index over train variables
    while (i < n) {
        if (i == test) {
            copy_instance(d, full_x[i], test_x);
            *test_y = full_y[i];
            i++;
        } else {
            copy_instance(d, full_x[i], train_x[j]);
            train_y[j] = full_y[i];
            i++;
            j++;
        }
    }
}

int loo_knn_experiment(int n, int d, double full_x[n][d], int full_y[n], int k, distance dist) {
    double train_x[n-1][d];
    int train_y[n-1];
    double test_x[d];
    int test_y;
    int correctly_classified = 0;
    for (int i = 0; i < n; i++) {
        split_train_test(i, n, d, full_x, full_y, train_x, train_y, test_x, &test_y);
        bool correct = false; // TODO!!! hier Ihren Klassifizierer einfügen!
        correctly_classified += (int) correct;
    }
    return correctly_classified;
}

void check_usage(int argc, char** argv) {
    if (argc != 6) {
        printf("usage: %s <n> <d> <filename.csv> <k> <distance-metric>\n", argv[0]);
        printf("<n> number of data points to be read\n");
        printf("<d> dimensionality of data points\n");
        printf("<filename.csv> contains the data to be classified (1st line will be ignored)\n");
        printf("<k> number of neighbours for majority voting\n");
        printf("<distance-metric>: must be \"manhattan\" or \"euclidean\"\n");
        exit(1);
    }
}

int main(int argc, char** argv) {
    check_usage(argc, argv);
    int n = atoi(argv[1]);
    int d = atoi(argv[2]);
    char* filename = argv[3];
    int k = atoi(argv[4]);
    distance dist = strcmp(argv[5], "manhattan") == 0 ? MANHATTAN : EUCLIDEAN;

    double x[n][d];
    int y[n];
    n = read_csv(filename, n, d, x, y);
    //print_csv(n, d, x, y);
    int correct = loo_knn_experiment(n, d, x, y, k, dist);
    printf("%d out of %d have been classified correctly (for a proportion of %f)\n", correct, n, (float) correct / n);
    return 0;
}