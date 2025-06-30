from abstract_syntax_tree import *
from analisador_lexico import AnalisadorLexico
from analisador_sintatico import AnalisadorSintatico
from analisador_semantico import AnalisadorSemantico
import traceback
import sys

DEBUG = False


def debug_print(*args, **kwargs):
    """Alias do print que só executa se DEBUG for True"""
    if DEBUG:
        print(*args, **kwargs)


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
            debug_print("DEBUG: Nó é None, retornando None")
            return None

        nome_metodo = f"interpretar_{type(no).__name__}"
        debug_print(f"DEBUG: Interpretando {no}")
        interpretador = getattr(self, nome_metodo, self.interpretador_generico)
        return interpretador(no)

    def interpretador_generico(self, no):
        raise InterpretadorError(
            f"Nenhum método interpretar_{type(no).__name__} definido"
        )

    def interpretar_ProgramaNode(self, no):
        debug_print(f"=== EXECUTANDO PROGRAMA: {no.nome} ===")

        if hasattr(no, "declaracoes") and no.declaracoes:
            if isinstance(no.declaracoes, DeclaracoesNode):
                debug_print("Processando declarações (DeclaracoesNode)")
                self.interpretar(no.declaracoes)
            else:
                debug_print(f"Processando {len(no.declaracoes)} declarações")
                for declaracao in no.declaracoes:
                    self.interpretar(declaracao)

        if hasattr(no, "bloco") and no.bloco:
            debug_print("Executando bloco principal")
            self.interpretar(no.bloco)

        debug_print("=== PROGRAMA FINALIZADO ===")

    def interpretar_DeclaracoesNode(self, no):
        """Interpreta o nó de declarações (lista de declarações)"""
        if hasattr(no, "declaracoes") and no.declaracoes:
            debug_print(f"Processando {len(no.declaracoes)} grupos de declarações")
            for declaracao in no.declaracoes:
                self.interpretar(declaracao)

    def interpretar_DeclaracaoVarNode(self, no):
        if (
            hasattr(no, "var_nodes")
            and no.var_nodes
            and hasattr(no, "tipo_node")
            and no.tipo_node
        ):
            tipo = no.tipo_node.valor
            debug_print(f"Declarando variáveis do tipo: {tipo}")

            for var_node in no.var_nodes:
                if var_node and hasattr(var_node, "valor"):
                    nome_var = var_node.valor

                    if tipo == "inteiro":
                        self.variaveis[nome_var] = 0
                    elif tipo == "lógico":
                        self.variaveis[nome_var] = False

                    self.tipos[nome_var] = tipo
                    debug_print(
                        f"  Variável '{nome_var}' declarada como {tipo} = {self.variaveis[nome_var]}"
                    )

    def interpretar_BlocoNode(self, no):
        if hasattr(no, "lista_comandos") and no.lista_comandos:
            if isinstance(no.lista_comandos, ListaComandosNode):
                debug_print(
                    f"Executando bloco com ListaComandosNode ({len(no.lista_comandos.comandos)} comandos)"
                )
                for i, comando in enumerate(no.lista_comandos.comandos):
                    if comando:
                        debug_print(f"  Comando {i+1}: {type(comando).__name__}")
                        self.interpretar(comando)
            else:
                debug_print(f"Executando bloco com {len(no.lista_comandos)} comandos")
                for i, comando in enumerate(no.lista_comandos):
                    if comando:
                        debug_print(f"  Comando {i+1}: {type(comando).__name__}")
                        self.interpretar(comando)

    def interpretar_ListaComandosNode(self, no):
        """Interpreta uma lista de comandos"""
        if hasattr(no, "comandos") and no.comandos:
            debug_print(f"Executando lista com {len(no.comandos)} comandos")
            for i, comando in enumerate(no.comandos):
                if comando:
                    debug_print(f"  Comando {i+1}: {type(comando).__name__}")
                    self.interpretar(comando)

    def interpretar_CompostoNode(self, no):
        """Interpreta um comando composto (início...fim)"""
        if hasattr(no, "lista_comandos") and no.lista_comandos:
            debug_print("Executando comando composto")
            if isinstance(no.lista_comandos, list):
                for i, comando in enumerate(no.lista_comandos):
                    if comando:
                        debug_print(f"  Comando {i+1}: {type(comando).__name__}")
                        self.interpretar(comando)
            else:
                self.interpretar(no.lista_comandos)

    def interpretar_AtribuicaoNode(self, no):
        if no.esquerda and no.direita:
            nome_var = no.esquerda.valor
            debug_print(f"ATRIBUIÇÃO: {nome_var} := ?")

            if nome_var not in self.variaveis:
                raise InterpretadorError(f"Variável '{nome_var}' não foi declarada")

            valor_antigo = self.variaveis[nome_var]
            valor = self.interpretar(no.direita)
            self.variaveis[nome_var] = valor

            debug_print(f"  {nome_var}: {valor_antigo} → {valor}")

    def interpretar_LerNode(self, no):
        if hasattr(no, "variaveis") and no.variaveis:
            debug_print(f"LEITURA de {len(no.variaveis)} variáveis")
            for variavel in no.variaveis:
                if variavel and hasattr(variavel, "valor"):
                    nome_var = variavel.valor

                    if nome_var not in self.variaveis:
                        raise InterpretadorError(
                            f"Variável '{nome_var}' não foi declarada"
                        )

                    try:
                        tipo_var = self.tipos[nome_var]
                        debug_print(f"  Lendo {nome_var} ({tipo_var})")

                        if tipo_var == "inteiro":
                            valor = int(input(""))
                        elif tipo_var == "lógico":
                            entrada = input("").lower()
                            valor = entrada == "1"
                        else:
                            valor = input("")

                        valor_antigo = self.variaveis[nome_var]
                        self.variaveis[nome_var] = valor
                        debug_print(f"    {nome_var}: {valor_antigo} → {valor}")

                    except ValueError:
                        raise InterpretadorError(
                            f"Valor inválido para variável '{nome_var}' do tipo {tipo_var}"
                        )

    def interpretar_EscreverNode(self, no):
        if hasattr(no, "expressoes") and no.expressoes:
            debug_print(f"ESCRITA de {len(no.expressoes)} expressões")
            saida = []

            for i, expr in enumerate(no.expressoes):
                if expr:
                    debug_print(f"  Expressão {i+1}: {type(expr).__name__}")
                    valor = self.interpretar(expr)
                    debug_print(f"    Resultado: {valor}")
                    saida.append(str(valor))

            resultado = "".join(saida)
            debug_print(f"SAÍDA: {resultado}")
            print(resultado)

    def interpretar_StringVarNode(self, no):
        if hasattr(no, "tipo"):
            if no.tipo == "string":
                valor = no.valor if hasattr(no, "valor") else ""
                debug_print(f"STRING LITERAL: '{valor}'")
                return valor
            elif no.tipo == "expr":
                debug_print("STRING EXPRESSÃO")
                if hasattr(no, "expr") and no.expr:
                    valor = self.interpretar(no.expr)
                    debug_print(f"  Valor da expressão: {valor}")
                    return str(valor)
        return ""

    def interpretar_SeNode(self, no):
        debug_print("ESTRUTURA CONDICIONAL (SE)")
        if no.condicao:
            debug_print("  Avaliando condição...")
            condicao_resultado = self.interpretar(no.condicao)
            debug_print(f"  Condição: {condicao_resultado}")

            if condicao_resultado:
                debug_print("  Executando ramo ENTÃO")
                if no.ramo_entao:
                    self.interpretar(no.ramo_entao)
            else:
                debug_print("  Executando ramo SENÃO")
                if hasattr(no, "ramo_senao") and no.ramo_senao:
                    self.interpretar(no.ramo_senao)

    def interpretar_EnquantoNode(self, no):
        debug_print("LOOP ENQUANTO")
        if no.condicao and no.corpo:
            iteracao = 0
            while True:
                iteracao += 1
                debug_print(f"  Iteração {iteracao}")
                debug_print("    Avaliando condição...")
                condicao_resultado = self.interpretar(no.condicao)
                debug_print(f"    Condição: {condicao_resultado}")

                if not condicao_resultado:
                    debug_print("  Loop finalizado")
                    break

                debug_print("    Executando corpo do loop")
                self.interpretar(no.corpo)

                if iteracao > 100:
                    debug_print("  AVISO: Loop executado mais de 100 vezes, parando")
                    break

    def interpretar_ExprLogicoNode(self, no):
        debug_print("EXPRESSÃO LÓGICA")
        if no.esquerda and no.direita and no.operador:
            if hasattr(no.operador, "valor"):
                operador_valor = no.operador.valor
            else:
                operador_valor = str(no.operador)

            debug_print(f"  Operador: {operador_valor}")

            esquerda = self.interpretar(no.esquerda)
            debug_print(f"  Operando esquerdo: {esquerda}")

            direita = self.interpretar(no.direita)
            debug_print(f"  Operando direito: {direita}")

            if operador_valor == "=":
                resultado = esquerda == direita
            elif operador_valor == "<>":
                resultado = esquerda != direita
            elif operador_valor == "<":
                resultado = esquerda < direita
            elif operador_valor == "<=":
                resultado = esquerda <= direita
            elif operador_valor == ">":
                resultado = esquerda > direita
            elif operador_valor == ">=":
                resultado = esquerda >= direita
            else:
                raise InterpretadorError(
                    f"Operador lógico desconhecido: {operador_valor}"
                )

            debug_print(
                f"  Resultado: {esquerda} {operador_valor} {direita} = {resultado}"
            )
            return resultado

        return False

    def interpretar_ExprLogicoSimpleNode(self, no):
        """Interpreta uma expressão lógica simples (apenas um ID)"""
        if hasattr(no, "id_node") and no.id_node:
            debug_print("EXPRESSÃO LÓGICA SIMPLES")
            valor = self.interpretar(no.id_node)
            debug_print(f"  Valor: {valor}")
            resultado = bool(valor)
            debug_print(f"  Resultado lógico: {resultado}")
            return resultado
        return False

    def interpretar_ExprNode(self, no):
        debug_print("EXPRESSÃO ARITMÉTICA")
        if hasattr(no, "termo") and no.termo:
            debug_print(f"  Interpretando termo...")
            termo_valor = self.interpretar(no.termo)
            debug_print(f"  Resultado do termo: {termo_valor}")

            if hasattr(no, "expr2") and no.expr2:
                debug_print(f"  Interpretando expr2...")
                expr2_resultado = self.interpretar_expr2_com_valor(
                    no.expr2, termo_valor
                )
                debug_print(f"  Resultado final da expressão: {expr2_resultado}")
                return expr2_resultado

            return termo_valor
        return 0

    def interpretar_TermoNode(self, no):
        debug_print("TERMO")
        if hasattr(no, "fator") and no.fator:
            debug_print(f"  Interpretando fator...")
            fator_valor = self.interpretar(no.fator)
            debug_print(f"  Resultado do fator: {fator_valor}")

            if hasattr(no, "termo2") and no.termo2:
                debug_print(f"  Interpretando termo2...")
                termo2_resultado = self.interpretar_termo2_com_valor(
                    no.termo2, fator_valor
                )
                debug_print(f"  Resultado final do termo: {termo2_resultado}")
                return termo2_resultado

            return fator_valor
        return 1

    def interpretar_FatorNode(self, no):
        if hasattr(no, "tipo"):
            debug_print(f"FATOR ({no.tipo})")

            if no.tipo == "parenteses":
                if hasattr(no, "expr") and no.expr:
                    debug_print("  Avaliando expressão entre parênteses")
                    return self.interpretar(no.expr)

            elif no.tipo == "negativo":
                if hasattr(no, "fator") and no.fator:
                    debug_print("  Aplicando negação")
                    valor = self.interpretar(no.fator)
                    resultado = -valor
                    debug_print(f"  -{valor} = {resultado}")
                    return resultado

            elif no.tipo == "id":
                if hasattr(no, "valor") and no.valor:
                    nome_var = no.valor
                    if nome_var not in self.variaveis:
                        raise InterpretadorError(
                            f"Variável '{nome_var}' não foi declarada"
                        )
                    valor = self.variaveis[nome_var]
                    debug_print(f"  Variável {nome_var} = {valor}")
                    return valor

            elif no.tipo == "num":
                if hasattr(no, "valor") and no.valor is not None:
                    debug_print(f"  Número: {no.valor}")
                    return no.valor

        return 0

    def interpretar_Expr2Node(self, no):
        debug_print("EXPR2 - Método legado (não deveria ser chamado diretamente)")
        if hasattr(no, "operador") and no.operador:
            termo_valor = (
                self.interpretar(no.termo) if hasattr(no, "termo") and no.termo else 0
            )
            operador = (
                no.operador.valor if hasattr(no.operador, "valor") else str(no.operador)
            )
            resto_valor = 0
            if hasattr(no, "expr2") and no.expr2:
                resto_valor = self.interpretar(no.expr2)

            if operador == "+":
                resultado = termo_valor + resto_valor
            elif operador == "-":
                resultado = termo_valor - resto_valor
            else:
                raise InterpretadorError(f"Operador desconhecido em Expr2: {operador}")

            return resultado
        else:
            return 0

    def interpretar_expr2_com_valor(self, expr2_no, valor_acumulado):
        if hasattr(expr2_no, "operador") and expr2_no.operador:
            debug_print("EXPR2 - Continuação de expressão com valor")

            termo_valor = (
                self.interpretar(expr2_no.termo)
                if hasattr(expr2_no, "termo") and expr2_no.termo
                else 0
            )
            debug_print(f"  Valor do termo: {termo_valor}")

            operador = (
                expr2_no.operador.valor
                if hasattr(expr2_no.operador, "valor")
                else str(expr2_no.operador)
            )
            debug_print(f"  Operador: {operador}")

            if operador == "+":
                resultado_parcial = valor_acumulado + termo_valor
            elif operador == "-":
                resultado_parcial = valor_acumulado - termo_valor
            else:
                raise InterpretadorError(f"Operador desconhecido em Expr2: {operador}")

            debug_print(
                f"  Operação: {valor_acumulado} {operador} {termo_valor} = {resultado_parcial}"
            )

            if hasattr(expr2_no, "expr2") and expr2_no.expr2:
                resultado_final = self.interpretar_expr2_com_valor(
                    expr2_no.expr2, resultado_parcial
                )
                return resultado_final
            else:
                return resultado_parcial
        else:
            debug_print("EXPR2 - Épsilon, retornando valor acumulado")
            return valor_acumulado

    def interpretar_termo2_com_valor(self, termo2_no, valor_acumulado):
        if hasattr(termo2_no, "operador") and termo2_no.operador:
            debug_print("TERMO2 - Continuação de termo com valor")

            fator_valor = (
                self.interpretar(termo2_no.fator)
                if hasattr(termo2_no, "fator") and termo2_no.fator
                else 1
            )
            debug_print(f"  Valor do fator: {fator_valor}")

            operador = (
                termo2_no.operador.valor
                if hasattr(termo2_no.operador, "valor")
                else str(termo2_no.operador)
            )
            debug_print(f"  Operador: {operador}")

            if operador == "*":
                resultado_parcial = valor_acumulado * fator_valor
            elif operador == "/":
                if fator_valor == 0:
                    raise InterpretadorError("Divisão por zero")
                resultado_parcial = valor_acumulado // fator_valor
            else:
                raise InterpretadorError(f"Operador desconhecido em Termo2: {operador}")

            debug_print(
                f"  Operação: {valor_acumulado} {operador} {fator_valor} = {resultado_parcial}"
            )

            if hasattr(termo2_no, "termo2") and termo2_no.termo2:
                resultado_final = self.interpretar_termo2_com_valor(
                    termo2_no.termo2, resultado_parcial
                )
                return resultado_final
            else:
                return resultado_parcial
        else:
            debug_print("TERMO2 - Épsilon, retornando valor acumulado")
            return valor_acumulado

    def interpretar_IdNode(self, no):
        if hasattr(no, "valor") and no.valor:
            nome_var = no.valor
            if nome_var not in self.variaveis:
                raise InterpretadorError(f"Variável '{nome_var}' não foi declarada")
            valor = self.variaveis[nome_var]
            debug_print(f"ID: {nome_var} = {valor}")
            return valor
        return 0

    def interpretar_OpLogicoNode(self, no):
        if hasattr(no, "valor"):
            return no.valor
        return None

    def interpretar_OpBinariaNode(self, no):
        debug_print("OPERAÇÃO BINÁRIA")
        debug_print(
            f"  Esquerda: {type(no.esquerda).__name__ if no.esquerda else None}"
        )
        debug_print(f"  Direita: {type(no.direita).__name__ if no.direita else None}")
        debug_print(f"  Operador: {no.op.valor if no.op else None}")

        if no.esquerda and no.direita and no.op:
            esquerda = self.interpretar(no.esquerda)
            debug_print(f"  Valor esquerdo: {esquerda}")

            direita = self.interpretar(no.direita)
            debug_print(f"  Valor direito: {direita}")

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

            debug_print(f"  Operação: {esquerda} {operador} {direita} = {resultado}")
            return resultado

        debug_print("  ERRO: Operação binária incompleta!")
        return 0

    def interpretar_OpUnariaNode(self, no):
        debug_print("OPERAÇÃO UNÁRIA")
        if no.expr and no.op:
            operador = no.op.valor
            debug_print(f"  Operador: {operador}")

            valor = self.interpretar(no.expr)
            debug_print(f"  Valor: {valor}")

            if operador == "-":
                resultado = -valor
            elif operador == "+":
                resultado = valor
            else:
                raise InterpretadorError(f"Operador unário desconhecido: {operador}")

            debug_print(f"  Resultado: {operador}{valor} = {resultado}")
            return resultado

        return 0

    def interpretar_VariavelNode(self, no):
        if hasattr(no, "valor") and no.valor:
            nome_var = no.valor

            if nome_var not in self.variaveis:
                raise InterpretadorError(f"Variável '{nome_var}' não foi declarada")

            valor = self.variaveis[nome_var]
            debug_print(f"VARIÁVEL: {nome_var} = {valor}")
            return valor

        return 0

    def interpretar_NumeroNode(self, no):
        if hasattr(no, "valor") and no.valor is not None:
            debug_print(f"NÚMERO: {no.valor}")
            return no.valor
        return 0

    def interpretar_StringNode(self, no):
        if hasattr(no, "valor") and no.valor:
            valor_limpo = no.valor.strip("\"'")
            debug_print(f"STRING: '{valor_limpo}'")
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
            debug_print("=== INICIANDO ANÁLISE LÉXICA ===")
            self.analisador_lexico = AnalisadorLexico(codigo_fonte)
            tokens = self.analisador_lexico.analisar()
            debug_print(f"Tokens gerados: {len(tokens)}")

            debug_print("\n=== INICIANDO ANÁLISE SINTÁTICA ===")
            self.analisador_sintatico = AnalisadorSintatico(tokens)
            arvore_sintatica = self.analisador_sintatico.analisar()

            if arvore_sintatica is None:
                raise Exception("Análise sintática falhou - árvore sintática é None")

            debug_print(f"AST raiz: {type(arvore_sintatica).__name__}")

            debug_print("\n=== INICIANDO ANÁLISE SEMÂNTICA ===")
            self.analisador_semantico.visitar(arvore_sintatica)
            debug_print("Análise semântica concluída")

            debug_print("\n=== INICIANDO INTERPRETAÇÃO ===")
            self.interpretador = Interpretador()
            self.interpretador.interpretar(arvore_sintatica)

            debug_print("\n=== ESTADO FINAL DAS VARIÁVEIS ===")
            for var, valor in self.interpretador.variaveis.items():
                tipo = self.interpretador.tipos.get(var, "desconhecido")
                debug_print(f"  {var} ({tipo}): {valor}")

            return True

        except Exception as e:
            print(f"\n=== ERRO DURANTE INTERPRETAÇÃO ===")
            print(f"Erro: {e}")
            traceback.print_exc()
            return False


if __name__ == "__main__":
    from read_code_file import read_code_file

    try:
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            with open(file_path, "r", encoding="utf-8") as file:
                codigo_fonte = file.read()
        else:
            raise Exception("No file path provided as argument.")

        executor = ExecutorInterpretador()
        sucesso = executor.interpretar_codigo(codigo_fonte)

        if sucesso:
            debug_print("\n=== INTERPRETAÇÃO CONCLUÍDA COM SUCESSO ===")
        else:
            debug_print("\n=== FALHA NA INTERPRETAÇÃO ===")

    except Exception as e:
        print(f"Erro: {e}")
