from analisador_lexico import AnalisadorLexico
from analisador_sintatico import AnalisadorSintatico
from read_code_file import read_code_file


codigos_para_ler = [
    "codigo1.txt",
    "codigo2.txt",
    "codigo3.txt",
    "codigo4.txt",
    "codigo5.txt",
]
for codigo in codigos_para_ler:
    try:
        codigo_fonte = read_code_file(codigo)
        analisador = AnalisadorLexico(codigo_fonte)
        tokens = analisador.analisar()
        analisador_sintatico = AnalisadorSintatico(tokens)
        arvore_sintatica = analisador_sintatico.analisar()
        print(f"Análise do código '{codigo}' concluída com sucesso.")
    except Exception as e:
        print(f"=== Erro durante a análise do código: {codigo}:")
        print(f"=== {e}")
