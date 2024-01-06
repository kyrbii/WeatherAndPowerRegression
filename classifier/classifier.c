#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <math.h>

//define some colors for our outputs - make them stand out :)
#define CNRM  "\x1B[0m"
#define CRED  "\x1B[31m"
#define CGRN  "\x1B[32m"
#define CYEL  "\x1B[33m"
#define CBLU  "\x1B[34m"
#define CMAG  "\x1B[35m"
#define CCYN  "\x1B[36m"
#define CWHT  "\x1B[37m"

//UNBEDINGT DIE KOMMENTARE PFLEGEN, EINIGE KOMMENTARE SAGEN SACHEN WIE NICHT FERTIG oder so, die wären bei der Abgabe ungünstig :)

/*
func iteriere durch alle Datensaetze durch und test/classify

    func trainingsdatensatz erstellen -> Volles File - (minus) Testdatensatz
    func classifier

        knn?

            -> fuer nn eigene methode, also dass des abgekapselt ist. ein einzelnes muss eh seperat betrachtet werden
            wenn knn, dann vielleicht einen durchschnittswert der k naechsten Nachbarn und keine Mehrheitsentscheid -> da Gleichheit sehr unwahrscheinlich ist!                
    func validator

        Ueberlegen. Implementieren wir eine Kulanz des validators, sodass wir Werte auf/abrunden bzw. eine range, also innerhalb von 5% oder so -> beim auf/abrunden kanns pasieren, dass der Wert weiter wegrutscht dur auf/abrundung
func main
*/


void ASSIGN_arg(char** argv, int* n, int* p, int* k, int* d_x, int* d_y, int* margin, char** f_x, char** f_y) {    //assigns the arguments given in the program call to the variables created in main
    *n = atoi(argv[1]);
    *p = atoi(argv[2]);
    *k = atoi(argv[3]);
    *margin = atoi(argv[4]);
    *f_x = argv[5];
    *d_x = atoi(argv[6]);
    *f_y = argv[7];
    *d_y = atoi(argv[8]);
}

bool TEST_arg(int argc,char** argv) { //check for usefullness of the programm call arguments via the argument count -> more to come
    if (argc == 9) {
        return true;
    }else { 
        printf("%sUse %s <n-rows> <p> <knn> <margin> <x-filename> <x-dimensions> <y-filename> <y-dimensions>\n\n"
               "<n-rows>\tbeing the number of lines/rows in both csv files (data-rows, i.e. wtithout header)\n"
               "<p>\t\tbeing the order of the minkowski distance (suggestion: 2)\n"
               "<knn>\t\tbeing the number of nearest neighbours to look at\n"
               "<margin>\tbeing the margin in whole percent with which the result is given\n"
               "<x-filename>\tbeing the name of the file whose data should be classified\n"
               "<x-dimensions>\tbeing the dimensions of the file containing the data\n"
               "<y-filename>\tbeing the file which contains the data, that is to match for the classifier\n"
               "<y-dimensions>\tbeing the dimensions of the file that is to match\n%s",CYEL,argv[0],CNRM);//What should be the arguments?
        return false;
    }
}

void ERROR_printnexit(bool validity, char* error_message, char* pass_message) {
    //checks for the validity of the first argument -> true means "you shall pass"
    if (validity == false) {
        printf("%s%s%s", CRED, error_message, CNRM);
        exit(1);
    }else {
        printf("%s%s%s", CGRN, pass_message, CNRM);
    }
}

int CSV_reader(char* filename, int n_rows, int dimensions, double data[n_rows][dimensions]) {
    //read the weather csv and write the values into our x array
    FILE* csv_file = fopen(filename,"r");
    bool search_succes = true;
        if (csv_file == NULL) {
            search_succes = false;
        }
    ERROR_printnexit(search_succes, "can't find filename for x\n", "found file x succesfully\n");

    //Read the first line into a dump variable, because we don't need it for the data
    {
        char dump_char;
        //read so many characters, till we reach the EOL
        while ((dump_char = fgetc(csv_file)) != 0x0D && dump_char != 0x0A);

        // if you createed the csv using only linefeed as a line-break, then COMMENT OUT the following
        fgetc(csv_file);
    }
    double dump_double;
    for (size_t i = 0; i < n_rows; i++) {
        for (size_t j = 0; j < (dimensions + 2); j++) {
            if (j <= 1) {
                fscanf(csv_file, "%lf,", &dump_double);
            }else {
                if (fscanf(csv_file, "%lf,", &data[i][(j - 2)]) == EOF) {
                    fclose(csv_file);
                    return i;
                }
            }
        }
    }
    fclose(csv_file);
    return n_rows;
}

void PRINTER(int n_rows, int dimensions, double data[n_rows][dimensions]){
    for (int i = 0; i < 1; i++) {   //watch out for the number of rows you print out. (psst ... 8670 are too much for the time you'd like to spend for this operation:)
        for (int j = 0; j < dimensions; j++) {
            printf("%lf, ", data[i][j]);  
        }
        printf("\n");
    }
}

void PRINT_result(int correct_count, int n_rows, int margin) {
    printf("Out of %d data samples %d were classified as correctly with a margin of %d%%. That makes a ratio of %.6f", n_rows, correct_count, margin, (float)correct_count/(float)n_rows);
}

int KNN_algorithm(int n_rows, int p_minkowski_distance, int k_neighbours, int dimensions_x, int dimensions_y, int margin, double x[n_rows][dimensions_x], double y[n_rows][dimensions_y]) {
    double training_x[n_rows-1][dimensions_x];
    double training_y[n_rows-1][dimensions_y];
    double testing_x[dimensions_x];
    double testing_y[dimensions_y];
    return;
}

int main(int argc, char* argv[]) {    //arc: argument count   argv: argument vector
    int n_rows, p_minkowski_distance, k_neighbours, dimensions_x, dimensions_y, margin;
    char *filename_x, *filename_y;
    
    //check for the right length of input argument vector and maybe in a later stage check for usefullness :)
    ERROR_printnexit(TEST_arg(argc, argv), "Invalid arguments for this classifier!\n", "Passed input tests\n");

    //assign all the arguments given in the programm call to our variables
    ASSIGN_arg(argv, &n_rows, &p_minkowski_distance, &k_neighbours, &dimensions_x, &dimensions_y, &margin, &filename_x, &filename_y);

    //create arrays for the content of our csv files
    double x[n_rows][dimensions_x];
    double y[n_rows][dimensions_y];
    int x_rows_temp, y_rows_temp;
    //now let's read our csv files and check if we read the same amount of rows in both files
    ERROR_printnexit((x_rows_temp = CSV_reader(filename_x, n_rows, dimensions_x, x)) == (y_rows_temp = CSV_reader(filename_y, n_rows, dimensions_y, y)), "Files can't be read with the same number of lines!\n", "Files passed the line-count test and are read in\n");
    n_rows = x_rows_temp;
    /*
    printf("Zuerst x/wetter\n");
    PRINTER(n_rows, dimensions_x, x);
    printf("Und jetzt x/die Stromsachen\n");
    PRINTER(n_rows, dimensions_y, y);
    */
    PRINT_result(KNN_algorithm(n_rows, p_minkowski_distance, k_neighbours, dimensions_x, dimensions_y, margin, x, y), n_rows, margin);
    return 0;
}
/*
func Fehlerueberpruefung in der Eingabe
    Test_arg -> eigentliche EIngaben

    kinda ready. No real error checking :)) - func ueberpruefen auf Fehler und zuweisen an die variablen

    Eingabe: .\classifier.exe n_rows p_minowski_distance k_neighbours .\weather.csv dimensions_x .\power.csv dimensions_y
    argv[0] = "classifier.exe"##
    argv[1] = "rows" n_rows##
    argv[2] = "value for p in the minkowski distance" p_minkowski_distance##
    argv[3] = "count of nearest neighbours" k_neighbours##
    argv[4] = "margin for k-neares neighbours in percent" margin ##
    argv[4] = "x-filename" 
    argv[5] = "dimensions of x" dimensions_x##
    argv[6] = "y-filename"
    argv[7] = "dimensions of y" d(y) dimensions_y ##

    .\classifier.exe 100 2 3 .\weather.csv 8000 .\power.csv 9000


## func csv-reader bauen -> überlegen, machen wir die ganze csv komplett, oder in Stuecken(Haelfte oder so), weil ultra riesig

## func csv-ausgeben fuer testen

*/