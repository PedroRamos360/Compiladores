import sys
from typing import Dict, Any, Optional, Union
from abstract_syntax_tree import *
from analisador_lexico import AnalisadorLexico
from analisador_sintatico import AnalisadorSintatico
from analisador_semantico import AnalisadorSemantico
import traceback
import sys

DEBUG = False


def debug_print(*args, **kwargs) -> None:
    if DEBUG:
        print(*args, **kwargs)


class InterpretadorError(Exception):
    def __init__(self, mensagem: str, token: Optional[Token] = None) -> None:
        self.mensagem = mensagem
        self.token = token
        super().__init__(self.mensagem)


class Interpretador:
    def __init__(self) -> None:
        self.variaveis: Dict[str, Any] = {}
        self.tipos: Dict[str, str] = {}

    def interpretar(self, no: Optional[ASTNode]) -> Any:
        if no is None:
            debug_print("DEBUG: Nó é None, retornando None")
            return None

        nome_metodo = f"interpretar_{type(no).__name__}"
        debug_print(f"DEBUG: Interpretando {no}")
        interpretador = getattr(self, nome_metodo, self.interpretador_generico)
        return interpretador(no)

    def interpretador_generico(self, no: ASTNode) -> None:
        raise InterpretadorError(
            f"Nenhum método interpretar_{type(no).__name__} definido"
        )

    def interpretar_ProgramaNode(self, no):
        debug_print(f"=== EXECUTANDO PROGRAMA: {no.nome} ===")

        if hasattr(no, "declaracoes") and no.declaracoes:
            debug_print("Processando declarações (DeclaracoesNode)")
            self.interpretar(no.declaracoes)

        debug_print("Executando bloco principal")
        self.interpretar(no.bloco)

        debug_print("=== PROGRAMA FINALIZADO ===")

    def interpretar_DeclaracoesNode(self, no):
        debug_print(f"Processando {len(no.declaracoes)} grupos de declarações")
        for declaracao in no.declaracoes:
            self.interpretar(declaracao)

    def interpretar_DeclaracaoVarNode(self, no):
        tipo = no.tipo_node.valor
        debug_print(f"Declarando variáveis do tipo: {tipo}")

        for var_node in no.var_nodes:
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
        debug_print(f"Executando bloco com {len(no.lista_comandos)} comandos")
        for i, comando in enumerate(no.lista_comandos):
            if comando:
                debug_print(f"  Comando {i+1}: {type(comando).__name__}")
                self.interpretar(comando)

    def interpretar_ListaComandosNode(self, no):
        debug_print(f"Executando lista com {len(no.comandos)} comandos")
        for i, comando in enumerate(no.comandos):
            debug_print(f"  Comando {i+1}: {type(comando).__name__}")
            self.interpretar(comando)

    def interpretar_AtribuicaoNode(self, no):
        nome_var = no.esquerda.valor
        debug_print(f"ATRIBUIÇÃO: {nome_var} := ?")
        valor_antigo = self.variaveis[nome_var]
        valor = self.interpretar(no.direita)
        self.variaveis[nome_var] = valor
        debug_print(f"  {nome_var}: {valor_antigo} → {valor}")

    def interpretar_LerNode(self, no):
        debug_print(f"LEITURA de {len(no.variaveis)} variáveis")
        for variavel in no.variaveis:
            if variavel and hasattr(variavel, "valor"):
                nome_var = variavel.valor
                try:
                    tipo_var = self.tipos[nome_var]
                    debug_print(f"  Lendo {nome_var} ({tipo_var})")

                    if tipo_var == "inteiro":
                        valor = int(input(""))
                    elif tipo_var == "lógico":
                        entrada = input("").lower()
                        valor = entrada == "1"
                    else:
                        raise InterpretadorError(
                            f"Tipo de variável '{tipo_var}' não suportado"
                        )

                    valor_antigo = self.variaveis[nome_var]
                    self.variaveis[nome_var] = valor
                    debug_print(f"    {nome_var}: {valor_antigo} → {valor}")

                except ValueError:
                    raise InterpretadorError(
                        f"Valor inválido para variável '{nome_var}' do tipo {tipo_var}"
                    )

    def interpretar_EscreverNode(self, no):
        debug_print(f"ESCRITA de {len(no.expressoes)} expressões")
        saida = []
        for i, expr in enumerate(no.expressoes):
            debug_print(f"  Expressão {i+1}: {type(expr).__name__}")
            valor = self.interpretar(expr)
            debug_print(f"    Resultado: {valor}")
            saida.append(str(valor))
        resultado = "".join(saida)
        debug_print(f"SAÍDA: {resultado}")
        print(resultado)

    def interpretar_StringVarNode(self, no):
        if no.tipo == "string":
            valor = no.valor
            debug_print(f"STRING LITERAL: '{valor}'")
            return valor
        elif no.tipo == "expr":
            debug_print("STRING EXPRESSÃO")
            valor = self.interpretar(no.expr)
            debug_print(f"  Valor da expressão: {valor}")
            return str(valor)

    def interpretar_SeNode(self, no):
        debug_print("ESTRUTURA CONDICIONAL (SE)")
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

    def interpretar_ExprLogicoNode(self, no):
        debug_print("EXPRESSÃO LÓGICA")
        operador_valor = no.operador.valor
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
            raise InterpretadorError(f"Operador lógico desconhecido: {operador_valor}")
        debug_print(f"  Resultado: {esquerda} {operador_valor} {direita} = {resultado}")
        return resultado

    def interpretar_ExprLogicoSimpleNode(self, no):
        debug_print("EXPRESSÃO LÓGICA SIMPLES")
        valor = self.interpretar(no.id_node)
        debug_print(f"  Valor: {valor}")
        resultado = bool(valor)
        debug_print(f"  Resultado lógico: {resultado}")
        return resultado

    def interpretar_ExprNode(self, no):
        debug_print("EXPRESSÃO ARITMÉTICA")
        termo_valor = self.interpretar(no.termo)
        debug_print(f"  Resultado do termo: {termo_valor}")
        if hasattr(no, "expr2") and no.expr2:
            debug_print(f"  Interpretando expr2...")
            expr2_resultado = self.interpretar_expr2_com_valor(no.expr2, termo_valor)
            debug_print(f"  Resultado final da expressão: {expr2_resultado}")
            return expr2_resultado

        return termo_valor

    def interpretar_TermoNode(self, no):
        debug_print("TERMO")
        fator_valor = self.interpretar(no.fator)
        debug_print(f"  Resultado do fator: {fator_valor}")
        if hasattr(no, "termo2") and no.termo2:
            debug_print(f"  Interpretando termo2...")
            termo2_resultado = self.interpretar_termo2_com_valor(no.termo2, fator_valor)
            debug_print(f"  Resultado final do termo: {termo2_resultado}")
            return termo2_resultado

        return fator_valor

    def interpretar_FatorNode(self, no):
        debug_print(f"FATOR ({no.tipo})")
        if no.tipo == "parenteses":
            debug_print("  Avaliando expressão entre parênteses")
            return self.interpretar(no.expr)
        elif no.tipo == "negativo":
            debug_print("  Aplicando negação")
            valor = self.interpretar(no.fator)
            resultado = -valor
            debug_print(f"  -{valor} = {resultado}")
            return resultado
        elif no.tipo == "id":
            nome_var = no.valor
            valor = self.variaveis[nome_var]
            debug_print(f"  Variável {nome_var} = {valor}")
            return valor
        elif no.tipo == "num":
            debug_print(f"  Número: {no.valor}")
            return no.valor

    def interpretar_expr2_com_valor(self, expr2_no, valor_acumulado):
        if hasattr(expr2_no, "operador") and expr2_no.operador:
            termo_valor = self.interpretar(expr2_no.termo)
            debug_print(f"  Valor do termo: {termo_valor}")
            operador = expr2_no.operador.valor
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
            return valor_acumulado

    def interpretar_termo2_com_valor(self, termo2_no, valor_acumulado):
        if hasattr(termo2_no, "operador") and termo2_no.operador:
            fator_valor = self.interpretar(termo2_no.fator)
            debug_print(f"  Valor do fator: {fator_valor}")
            operador = termo2_no.operador.valor
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
            return valor_acumulado

    def interpretar_IdNode(self, no):
        nome_var = no.valor
        valor = self.variaveis[nome_var]
        debug_print(f"ID: {nome_var} = {valor}")
        return valor

    def interpretar_OpLogicoNode(self, no):
        return no.valor

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
        debug_print(f"NÚMERO: {no.valor}")
        return no.valor


class ExecutorInterpretador:
    def __init__(self) -> None:
        self.analisador_lexico: Optional[AnalisadorLexico] = None
        self.analisador_sintatico: Optional[AnalisadorSintatico] = None
        self.analisador_semantico = AnalisadorSemantico()
        self.interpretador: Optional[Interpretador] = None

    def interpretar_codigo(self, codigo_fonte: str) -> bool:
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
