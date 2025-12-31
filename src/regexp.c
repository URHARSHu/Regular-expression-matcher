#include <stdio.h>
int match(char *regexp, char *text);
int mactchhere(char *regexp , char *text);
int matchstar(int c, char *regexp, char *text);
int match(char *regexp, char *text){
    if (regexp[0]=='^')
        return mactchhere(regexp+1,text);   
    do {
        if (mactchhere(regexp,text))
            return 1;       
}   while (*text++ != '\0');
    return 0;
}  
int mactchhere(char *regexp , char *text){
    if (regexp[0]=='\0')
        return 1;
    if (regexp[1]=='*')
        return matchstar(regexp[0],regexp+2,text);
    if (regexp[0]=='$' && regexp[1]=='\0')
        return *text=='\0';
    if (*text!='\0' && (regexp[0]=='.' || regexp[0]==*text))
        return mactchhere(regexp+1,text+1);
    return 0;
}   
int matchstar(int c, char *regexp, char *text){
    do {
        if (mactchhere(regexp,text))
            return 1;
    } while (*text!='\0' && (*text++==c || c=='.'));
    return 0;
}
/* Example usage */
int main() {
    char regexp[50] ;char text[50];
    printf("Enter regexp and text: ");
    fflush(stdout);
    scanf("%s %s", regexp, text);

    if (match(regexp, text)) {
        printf("Match found!\n");
    } else {
        printf("No match.\n");
    return 0;
    }
}