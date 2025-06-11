from analisador_lexico import AnalisadorLexico
from analisador_sintatico import AnalisadorSintatico
from read_code_file import read_code_file


codigo_fonte = read_code_file("codigo1.txt")
print(codigo_fonte)
analisador = AnalisadorLexico(codigo_fonte)


tokens = analisador.analisar()

analisador_sintatico = AnalisadorSintatico(tokens)
try:
    arvore_sintatica = analisador_sintatico.analisar()
    print("Análise sintática concluída com sucesso!")

except SyntaxError as e:
    print(f"Erro de Sintaxe: {e}")
