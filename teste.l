%{
#include <stdio.h>
%}

%%

[0-9]+  { printf("Número: %s\n", yytext); }
[ \t\n] { /* Ignora espaços, tabs e quebras de linha */ }
.       { printf("Caractere: %s\n", yytext); }

%%

int main() {
    yylex();
    return 0;
}

int yywrap() {
    return 1;
}
