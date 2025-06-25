from abstract_syntax_tree import *
from analisador_lexico import AnalisadorLexico
from analisador_sintatico import AnalisadorSintatico
from analisador_semantico import AnalisadorSemantico
import traceback


class InterpretadorError(Exception):
    def __init__(self, mensagem, token=None):
        self.mensagem = mensagem
        self.token = token
        super().__init__(self.mensagem)


class Interpretador:
    def __init__(self):
        self.variaveis = {}
        self.tipos = {}

    def interpretar(self, no):
        if no is None:
            print("DEBUG: Nó é None, retornando None")
            return None

        nome_metodo = f"interpretar_{type(no).__name__}"
        print(f"DEBUG: Interpretando {no}")
        interpretador = getattr(self, nome_metodo, self.interpretador_generico)
        return interpretador(no)

    def interpretador_generico(self, no):
        raise InterpretadorError(
            f"Nenhum método interpretar_{type(no).__name__} definido"
        )

    def interpretar_ProgramaNode(self, no):
        print(f"=== EXECUTANDO PROGRAMA: {no.nome} ===")

        if hasattr(no, "declaracoes") and no.declaracoes:
            print(f"Processando {len(no.declaracoes)} declarações")
            for declaracao in no.declaracoes:
                self.interpretar(declaracao)

        if hasattr(no, "bloco") and no.bloco:
            print("Executando bloco principal")
            self.interpretar(no.bloco)

        print("=== PROGRAMA FINALIZADO ===")

    def interpretar_DeclaracaoVarNode(self, no):
        if (
            hasattr(no, "var_nodes")
            and no.var_nodes
            and hasattr(no, "tipo_node")
            and no.tipo_node
        ):
            tipo = no.tipo_node.valor
            print(f"Declarando variáveis do tipo: {tipo}")

            for var_node in no.var_nodes:
                if var_node and hasattr(var_node, "valor"):
                    nome_var = var_node.valor

                    if tipo == "inteiro":
                        self.variaveis[nome_var] = 0
                    elif tipo == "lógico":
                        self.variaveis[nome_var] = False

                    self.tipos[nome_var] = tipo
                    print(
                        f"  Variável '{nome_var}' declarada como {tipo} = {self.variaveis[nome_var]}"
                    )

    def interpretar_BlocoNode(self, no):
        if hasattr(no, "lista_comandos") and no.lista_comandos:
            print(f"Executando bloco com {len(no.lista_comandos)} comandos")
            for i, comando in enumerate(no.lista_comandos):
                if comando:
                    print(f"  Comando {i+1}: {type(comando).__name__}")
                    self.interpretar(comando)

    def interpretar_AtribuicaoNode(self, no):
        if no.esquerda and no.direita:
            nome_var = no.esquerda.valor
            print(f"ATRIBUIÇÃO: {nome_var} := ?")

            if nome_var not in self.variaveis:
                raise InterpretadorError(f"Variável '{nome_var}' não foi declarada")

            valor_antigo = self.variaveis[nome_var]
            valor = self.interpretar(no.direita)
            self.variaveis[nome_var] = valor

            print(f"  {nome_var}: {valor_antigo} → {valor}")

    def interpretar_LerNode(self, no):
        if hasattr(no, "variaveis") and no.variaveis:
            print(f"LEITURA de {len(no.variaveis)} variáveis")
            for variavel in no.variaveis:
                if variavel and hasattr(variavel, "valor"):
                    nome_var = variavel.valor

                    if nome_var not in self.variaveis:
                        raise InterpretadorError(
                            f"Variável '{nome_var}' não foi declarada"
                        )

                    try:
                        tipo_var = self.tipos[nome_var]
                        print(f"  Lendo {nome_var} ({tipo_var})")

                        if tipo_var == "inteiro":
                            valor = int(input(""))
                        elif tipo_var == "lógico":
                            entrada = input("").lower()
                            valor = entrada == "1"
                        else:
                            valor = input("")

                        valor_antigo = self.variaveis[nome_var]
                        self.variaveis[nome_var] = valor
                        print(f"    {nome_var}: {valor_antigo} → {valor}")

                    except ValueError:
                        raise InterpretadorError(
                            f"Valor inválido para variável '{nome_var}' do tipo {tipo_var}"
                        )

    def interpretar_EscreverNode(self, no):
        if hasattr(no, "expressoes") and no.expressoes:
            print(f"ESCRITA de {len(no.expressoes)} expressões")
            saida = []

            for i, expr in enumerate(no.expressoes):
                if expr:
                    print(f"  Expressão {i+1}: {type(expr).__name__}")
                    valor = self.interpretar(expr)
                    print(f"    Resultado: {valor}")
                    saida.append(str(valor))

            resultado = "".join(saida)
            print(f"SAÍDA: {resultado}")
            print(resultado)

    def interpretar_SeNode(self, no):
        print("ESTRUTURA CONDICIONAL (SE)")
        if no.condicao:
            print("  Avaliando condição...")
            condicao_resultado = self.interpretar(no.condicao)
            print(f"  Condição: {condicao_resultado}")

            if condicao_resultado:
                print("  Executando ramo ENTÃO")
                if no.ramo_entao:
                    self.interpretar(no.ramo_entao)
            else:
                print("  Executando ramo SENÃO")
                if hasattr(no, "ramo_senao") and no.ramo_senao:
                    self.interpretar(no.ramo_senao)

    def interpretar_EnquantoNode(self, no):
        print("LOOP ENQUANTO")
        if no.condicao and no.corpo:
            iteracao = 0
            while True:
                iteracao += 1
                print(f"  Iteração {iteracao}")
                print("    Avaliando condição...")
                condicao_resultado = self.interpretar(no.condicao)
                print(f"    Condição: {condicao_resultado}")

                if not condicao_resultado:
                    print("  Loop finalizado")
                    break

                print("    Executando corpo do loop")
                self.interpretar(no.corpo)

                if iteracao > 100:  # Proteção contra loop infinito
                    print("  AVISO: Loop executado mais de 100 vezes, parando")
                    break

    def interpretar_ExprLogicoNode(self, no):
        print("EXPRESSÃO LÓGICA")
        if no.esquerda and no.direita and no.operador:
            print(f"  Operador: {no.operador.valor}")

            esquerda = self.interpretar(no.esquerda)
            print(f"  Operando esquerdo: {esquerda}")

            direita = self.interpretar(no.direita)
            print(f"  Operando direito: {direita}")

            operador = no.operador.valor

            if operador == "=":
                resultado = esquerda == direita
            elif operador == "<>":
                resultado = esquerda != direita
            elif operador == "<":
                resultado = esquerda < direita
            elif operador == "<=":
                resultado = esquerda <= direita
            elif operador == ">":
                resultado = esquerda > direita
            elif operador == ">=":
                resultado = esquerda >= direita
            else:
                raise InterpretadorError(f"Operador lógico desconhecido: {operador}")

            print(f"  Resultado: {esquerda} {operador} {direita} = {resultado}")
            return resultado

        return False

    def interpretar_ExprNode(self, no):
        print("EXPRESSÃO ARITMÉTICA")
        if hasattr(no, "termo") and no.termo:
            print(f"  Termo: {no}")
            resultado = self.interpretar(no.termo)
            print(f"  Resultado do termo: {resultado}")

            if hasattr(no, "expr2") and no.expr2:
                print(f"  Expr2: {type(no.expr2).__name__}")
                if hasattr(no.expr2, "direita"):
                    print(f"    Expr2.direita: {no.expr2.direita}")
                if hasattr(no.expr2, "esquerda"):
                    print(
                        f"    Expr2.esquerda: {no.expr2.esquerda if no.expr2.esquerda else None}"
                    )
                if hasattr(no.expr2, "op"):
                    print(f"    Expr2.op: {no.expr2.op.valor if no.expr2.op else None}")

                expr2_resultado = self.interpretar(no.expr2)
                print(f"  Resultado da expr2: {expr2_resultado}")
                return expr2_resultado

            return resultado
        return 0

    def interpretar_TermoNode(self, no):
        print("TERMO")
        if hasattr(no, "fator") and no.fator:
            print(f"  Fator: {no}")
            resultado = self.interpretar(no.fator)
            print(f"  Resultado do fator: {resultado}")

            if hasattr(no, "termo2") and no.termo2:
                print(f"  Termo2: {type(no.termo2).__name__}")
                termo2_resultado = self.interpretar(no.termo2)
                print(f"  Resultado do termo2: {termo2_resultado}")
                return termo2_resultado

            return resultado
        return 0

    def interpretar_OpBinariaNode(self, no):
        print("OPERAÇÃO BINÁRIA")
        print(f"  Esquerda: {type(no.esquerda).__name__ if no.esquerda else None}")
        print(f"  Direita: {type(no.direita).__name__ if no.direita else None}")
        print(f"  Operador: {no.op.valor if no.op else None}")

        if no.esquerda and no.direita and no.op:
            esquerda = self.interpretar(no.esquerda)
            print(f"  Valor esquerdo: {esquerda}")

            direita = self.interpretar(no.direita)
            print(f"  Valor direito: {direita}")

            operador = no.op.valor

            if operador == "+":
                resultado = esquerda + direita
            elif operador == "-":
                resultado = esquerda - direita
            elif operador == "*":
                resultado = esquerda * direita
            elif operador == "/":
                if direita == 0:
                    raise InterpretadorError("Divisão por zero")
                resultado = esquerda // direita
            else:
                raise InterpretadorError(f"Operador binário desconhecido: {operador}")

            print(f"  Operação: {esquerda} {operador} {direita} = {resultado}")
            return resultado

        print("  ERRO: Operação binária incompleta!")
        return 0

    def interpretar_OpUnariaNode(self, no):
        print("OPERAÇÃO UNÁRIA")
        if no.expr and no.op:
            operador = no.op.valor
            print(f"  Operador: {operador}")

            valor = self.interpretar(no.expr)
            print(f"  Valor: {valor}")

            if operador == "-":
                resultado = -valor
            elif operador == "+":
                resultado = valor
            else:
                raise InterpretadorError(f"Operador unário desconhecido: {operador}")

            print(f"  Resultado: {operador}{valor} = {resultado}")
            return resultado

        return 0

    def interpretar_VariavelNode(self, no):
        if hasattr(no, "valor") and no.valor:
            nome_var = no.valor

            if nome_var not in self.variaveis:
                raise InterpretadorError(f"Variável '{nome_var}' não foi declarada")

            valor = self.variaveis[nome_var]
            print(f"VARIÁVEL: {nome_var} = {valor}")
            return valor

        return 0

    def interpretar_NumeroNode(self, no):
        if hasattr(no, "valor") and no.valor is not None:
            print(f"NÚMERO: {no.valor}")
            return no.valor
        return 0

    def interpretar_StringNode(self, no):
        if hasattr(no, "valor") and no.valor:
            valor_limpo = no.valor.strip("\"'")
            print(f"STRING: '{valor_limpo}'")
            return valor_limpo
        return ""

    def interpretar_TipoNode(self, no):
        pass


class ExecutorInterpretador:
    def __init__(self):
        self.analisador_lexico = None
        self.analisador_sintatico = None
        self.analisador_semantico = AnalisadorSemantico()
        self.interpretador = None

    def interpretar_codigo(self, codigo_fonte):
        try:
            print("=== INICIANDO ANÁLISE LÉXICA ===")
            self.analisador_lexico = AnalisadorLexico(codigo_fonte)
            tokens = self.analisador_lexico.analisar()
            print(f"Tokens gerados: {len(tokens)}")

            print("\n=== INICIANDO ANÁLISE SINTÁTICA ===")
            self.analisador_sintatico = AnalisadorSintatico(tokens)
            arvore_sintatica = self.analisador_sintatico.analisar()

            if arvore_sintatica is None:
                raise Exception("Análise sintática falhou - árvore sintática é None")

            print(f"AST raiz: {type(arvore_sintatica).__name__}")

            print("\n=== INICIANDO ANÁLISE SEMÂNTICA ===")
            self.analisador_semantico.visitar(arvore_sintatica)
            print("Análise semântica concluída")

            print("\n=== INICIANDO INTERPRETAÇÃO ===")
            self.interpretador = Interpretador()
            self.interpretador.interpretar(arvore_sintatica)

            print("\n=== ESTADO FINAL DAS VARIÁVEIS ===")
            for var, valor in self.interpretador.variaveis.items():
                tipo = self.interpretador.tipos.get(var, "desconhecido")
                print(f"  {var} ({tipo}): {valor}")

            return True

        except Exception as e:
            print(f"\n=== ERRO DURANTE INTERPRETAÇÃO ===")
            print(f"Erro: {e}")
            traceback.print_exc()
            return False


if __name__ == "__main__":
    from read_code_file import read_code_file

    try:
        codigo_fonte = read_code_file("codigo1.txt")

        executor = ExecutorInterpretador()
        sucesso = executor.interpretar_codigo(codigo_fonte)

        if sucesso:
            print("\n=== INTERPRETAÇÃO CONCLUÍDA COM SUCESSO ===")
        else:
            print("\n=== FALHA NA INTERPRETAÇÃO ===")

    except Exception as e:
        print(f"Erro: {e}")
