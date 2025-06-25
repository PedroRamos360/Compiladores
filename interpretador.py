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
            return None

        nome_metodo = f"interpretar_{type(no).__name__}"
        interpretador = getattr(self, nome_metodo, self.interpretador_generico)
        return interpretador(no)

    def interpretador_generico(self, no):
        raise InterpretadorError(
            f"Nenhum método interpretar_{type(no).__name__} definido"
        )

    def interpretar_ProgramaNode(self, no):
        print(f"Executando programa: {no.nome}")

        if hasattr(no, "declaracoes") and no.declaracoes:
            for declaracao in no.declaracoes:
                self.interpretar(declaracao)

        if hasattr(no, "bloco") and no.bloco:
            self.interpretar(no.bloco)

        print("Programa finalizado.")

    def interpretar_DeclaracaoVarNode(self, no):
        if (
            hasattr(no, "var_nodes")
            and no.var_nodes
            and hasattr(no, "tipo_node")
            and no.tipo_node
        ):
            tipo = no.tipo_node.valor

            for var_node in no.var_nodes:
                if var_node and hasattr(var_node, "valor"):
                    nome_var = var_node.valor

                    if tipo == "inteiro":
                        self.variaveis[nome_var] = 0
                    elif tipo == "lógico":
                        self.variaveis[nome_var] = False

                    self.tipos[nome_var] = tipo
                    print(f"Variável '{nome_var}' declarada como {tipo}")

    def interpretar_BlocoNode(self, no):
        if hasattr(no, "lista_comandos") and no.lista_comandos:
            for comando in no.lista_comandos:
                if comando:
                    self.interpretar(comando)

    def interpretar_AtribuicaoNode(self, no):
        if no.esquerda and no.direita:
            nome_var = no.esquerda.valor

            if nome_var not in self.variaveis:
                raise InterpretadorError(f"Variável '{nome_var}' não foi declarada")

            valor = self.interpretar(no.direita)

            self.variaveis[nome_var] = valor
            print(f"Atribuição: {nome_var} = {valor}")

    def interpretar_LerNode(self, no):
        if hasattr(no, "variaveis") and no.variaveis:
            for variavel in no.variaveis:
                if variavel and hasattr(variavel, "valor"):
                    nome_var = variavel.valor

                    if nome_var not in self.variaveis:
                        raise InterpretadorError(
                            f"Variável '{nome_var}' não foi declarada"
                        )

                    try:
                        tipo_var = self.tipos[nome_var]
                        if tipo_var == "inteiro":
                            valor = int(
                                input(f"Digite um valor inteiro para {nome_var}: ")
                            )
                        elif tipo_var == "lógico":
                            entrada = input(
                                f"Digite verdadeiro/falso para {nome_var}: "
                            ).lower()
                            valor = entrada in ["verdadeiro", "true", "1", "sim"]
                        else:
                            valor = input(f"Digite um valor para {nome_var}: ")

                        self.variaveis[nome_var] = valor
                        print(f"Leitura: {nome_var} = {valor}")

                    except ValueError:
                        raise InterpretadorError(
                            f"Valor inválido para variável '{nome_var}' do tipo {tipo_var}"
                        )

    def interpretar_EscreverNode(self, no):
        if hasattr(no, "expressoes") and no.expressoes:
            saida = []

            for expr in no.expressoes:
                if expr:
                    valor = self.interpretar(expr)
                    saida.append(str(valor))

            resultado = "".join(saida)
            print(resultado)

    def interpretar_SeNode(self, no):
        if no.condicao:
            condicao_resultado = self.interpretar(no.condicao)

            if condicao_resultado:
                print("Executando ramo ENTÃO")
                if no.ramo_entao:
                    self.interpretar(no.ramo_entao)
            else:
                print("Executando ramo SENÃO")
                if hasattr(no, "ramo_senao") and no.ramo_senao:
                    self.interpretar(no.ramo_senao)

    def interpretar_EnquantoNode(self, no):
        """Interpreta loops while."""
        if no.condicao and no.corpo:
            contador_iteracoes = 0
            max_iteracoes = 10000

            while True:
                contador_iteracoes += 1
                if contador_iteracoes > max_iteracoes:
                    raise InterpretadorError(
                        "Loop infinito detectado - mais de 10000 iterações"
                    )

                condicao_resultado = self.interpretar(no.condicao)
                print(
                    f"Condição do loop (iteração {contador_iteracoes}): {condicao_resultado}"
                )

                if not condicao_resultado:
                    break

                self.interpretar(no.corpo)

            print(f"Loop finalizado após {contador_iteracoes-1} iterações")

    def interpretar_ExprLogicoNode(self, no):
        if no.esquerda and no.direita and no.operador:
            esquerda = self.interpretar(no.esquerda)
            direita = self.interpretar(no.direita)
            operador = no.operador.valor

            print(f"Comparação: {esquerda} {operador} {direita}")

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

            print(f"Resultado da comparação: {resultado}")
            return resultado

        return False

    def interpretar_ExprNode(self, no):
        print(f"DEBUG ExprNode: termo={type(no.termo).__name__ if hasattr(no, 'termo') and no.termo else None}")
        print(f"DEBUG ExprNode: expr2={type(no.expr2).__name__ if hasattr(no, 'expr2') and no.expr2 else None}")
        
        if hasattr(no, "termo") and no.termo:
            resultado = self.interpretar(no.termo)
            print(f"Resultado do termo: {resultado}")

            if hasattr(no, "expr2") and no.expr2:
                expr2_resultado = self.interpretar(no.expr2)
                print(f"Resultado da expr2: {expr2_resultado}")
                return expr2_resultado

            return resultado
        return 0

    def interpretar_TermoNode(self, no):
        print(f"DEBUG TermoNode: fator={type(no.fator).__name__ if hasattr(no, 'fator') and no.fator else None}")
        print(f"DEBUG TermoNode: termo2={type(no.termo2).__name__ if hasattr(no, 'termo2') and no.termo2 else None}")
        
        if hasattr(no, "fator") and no.fator:
            resultado = self.interpretar(no.fator)
            print(f"Resultado do fator: {resultado}")

            if hasattr(no, "termo2") and no.termo2:
                termo2_resultado = self.interpretar(no.termo2)
                print(f"Resultado do termo2: {termo2_resultado}")
                return termo2_resultado

            return resultado
        return 0


    def interpretar_OpBinariaNode(self, no):
        print(f"DEBUG OpBinariaNode: esquerda={type(no.esquerda).__name__ if no.esquerda else None}")
        print(f"DEBUG OpBinariaNode: direita={type(no.direita).__name__ if no.direita else None}")
        print(f"DEBUG OpBinariaNode: op={no.op.valor if no.op else None}")
        
        if no.esquerda and no.direita and no.op:
            esquerda = self.interpretar(no.esquerda)
            direita = self.interpretar(no.direita)
            operador = no.op.valor

            print(f"Operação: {esquerda} {operador} {direita}")

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

            print(f"Resultado: {resultado}")
            return resultado

        print("DEBUG OpBinariaNode: Um dos operandos ou operador é None!")
        return 0

    def interpretar_OpUnariaNode(self, no):
        if no.expr and no.op:
            valor = self.interpretar(no.expr)
            operador = no.op.valor

            if operador == "-":
                resultado = -valor
            elif operador == "+":
                resultado = valor
            else:
                raise InterpretadorError(f"Operador unário desconhecido: {operador}")

            print(f"Operação unária: {operador}{valor} = {resultado}")
            return resultado

        return 0

    def interpretar_VariavelNode(self, no):
        if hasattr(no, "valor") and no.valor:
            nome_var = no.valor

            if nome_var not in self.variaveis:
                raise InterpretadorError(f"Variável '{nome_var}' não foi declarada")

            valor = self.variaveis[nome_var]
            print(f"Acesso à variável: {nome_var} = {valor}")
            return valor

        return 0

    def interpretar_NumeroNode(self, no):
        if hasattr(no, "valor") and no.valor is not None:
            print(f"Número literal: {no.valor}")
            return no.valor
        return 0

    def interpretar_StringNode(self, no):
        if hasattr(no, "valor") and no.valor:
            valor_limpo = no.valor.strip("\"'")
            print(f"String literal: '{valor_limpo}'")
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
            self.analisador_lexico = AnalisadorLexico(codigo_fonte)
            tokens = self.analisador_lexico.analisar()
            self.analisador_sintatico = AnalisadorSintatico(tokens)
            arvore_sintatica = self.analisador_sintatico.analisar()
            if arvore_sintatica is None:
                raise Exception("Análise sintática falhou - árvore sintática é None")
            self.analisador_semantico.visitar(arvore_sintatica)
            self.interpretador = Interpretador()
            self.interpretador.interpretar(arvore_sintatica)
            return True

        except Exception as e:

            traceback.print_exc()
            return False


if __name__ == "__main__":
    from read_code_file import read_code_file

    try:
        codigo_fonte = read_code_file("codigo1.txt")

        executor = ExecutorInterpretador()
        sucesso = executor.interpretar_codigo(codigo_fonte)

        if sucesso:
            print("Interpretação concluída com sucesso!")
        else:
            print("Falha na interpretação")

    except Exception as e:
        print(f"Erro: {e}")
