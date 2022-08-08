#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// typedef struct string {
//     char *content;
// } string, *pString;

// #define STR_DEFUALT_SIZE 128

// pString string_init(char *text) {
//     int len = strlen(text);
//     pString str = (pString)malloc(sizeof(string));
//     if (len > STR_DEFUALT_SIZE) {
//         str->content = (char *)malloc(sizeof(char) * len * 2);
//     } else {
//         str->content = (char *)malloc(STR_DEFUALT_SIZE);
//     }
// }

// void string_destroy(pString &){

// }

int main() {
    int x = 0;
    char *text = "some text";
    printf("%s", text + x);
    return 0;
}