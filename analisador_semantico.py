from abstract_syntax_tree import *
from tabela_de_simbolos import TabelaDeSimbolos, Simbolo

class SemanticError(Exception):
    def __init__(self, mensagem, token=None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.token = token

    def __str__(self):
        if self.token:
            return f'Erro Semântico: {self.mensagem} na linha {self.token.linha}, coluna {self.token.coluna}'
        return f'Erro Semântico: {self.mensagem}'


class AnalisadorSemantico:
    def __init__(self):
        self.tabela_de_simbolos = TabelaDeSimbolos()

    def visitar(self, no):
        nome_metodo = f"visitar_{type(no).__name__}"
        visitante = getattr(self, nome_metodo, self.visitante_generico)
        return visitante(no)

    def visitante_generico(self, no):
        raise Exception(f"Nenhum método visitar_{type(no).__name__} definido")

    def visitar_ProgramaNode(self, no):
        for declaracao in no.declaracoes:
            self.visitar(declaracao)
        self.visitar(no.bloco)

    def visitar_BlocoNode(self, no):
        for comando in no.lista_comandos:
            self.visitar(comando)

    def visitar_DeclaracaoVarNode(self, no):
        nome_tipo = no.tipo_node.valor
        for no_var in no.var_nodes:
            nome_variavel = no_var.valor
            if self.tabela_de_simbolos.buscar(nome_variavel):
                raise SemanticError(f"Variável '{nome_variavel}' já declarada.", token=no_var.token)
            simbolo = Simbolo(nome_variavel, nome_tipo)
            self.tabela_de_simbolos.definir(simbolo)

    def visitar_AtribuicaoNode(self, no):
        no_variavel = no.esquerda
        simbolo = self.tabela_de_simbolos.buscar(no_variavel.valor)
        if not simbolo:
            raise SemanticError(f"Variável '{no_variavel.valor}' não declarada.", token=no_variavel.token)

        tipo_expressao = self.visitar(no.direita)

        if simbolo.tipo != tipo_expressao:
            raise SemanticError(
                f"Incompatibilidade de tipos. Não é possível atribuir '{tipo_expressao}' para a variável '{no_variavel.valor}' do tipo '{simbolo.tipo}'.",
                token=no.op
            )

    def visitar_VariavelNode(self, no):
        nome_variavel = no.valor
        simbolo = self.tabela_de_simbolos.buscar(nome_variavel)
        if not simbolo:
            raise SemanticError(f"Variável '{nome_variavel}' não declarada.", token=no.token)
        return simbolo.tipo

    def visitar_NumeroNode(self, no):
        return "inteiro"

    def visitar_ExprLogicoNode(self, no):
        tipo_esquerda = self.visitar(no.esquerda)
        tipo_direita = self.visitar(no.direita)
        if tipo_esquerda != tipo_direita:
            raise SemanticError(
                f"Tipos incompatíveis na expressão lógica ('{tipo_esquerda}' e '{tipo_direita}').",
                token=no.operador
            )
        return "lógico"

    def visitar_OpBinariaNode(self, no):
        tipo_esquerda = self.visitar(no.esquerda)
        tipo_direita = self.visitar(no.direita)
        if tipo_esquerda != "inteiro" or tipo_direita != "inteiro":
            raise SemanticError(
                "Operações aritméticas só podem ser realizadas em inteiros.",
                token=no.op
            )
        return "inteiro"

    def visitar_OpUnariaNode(self, no):
        tipo_expr = self.visitar(no.expr)
        if tipo_expr != "inteiro":
            raise SemanticError(
                "Operação unária de negação só pode ser aplicada a inteiros.",
                token=no.op
            )
        return "inteiro"

    def visitar_SeNode(self, no):
        tipo_condicao = self.visitar(no.condicao)
        if tipo_condicao != "lógico":
            raise SemanticError("A condição do 'se' deve ser uma expressão lógica.")
        self.visitar(no.ramo_entao)
        if no.ramo_senao:
            self.visitar(no.ramo_senao)

    def visitar_EnquantoNode(self, no):
        tipo_condicao = self.visitar(no.condicao)
        if tipo_condicao != "lógico":
            raise SemanticError("A condição do 'enquanto' deve ser uma expressão lógica.",)
        self.visitar(no.corpo)

    def visitar_LerNode(self, no):
        for variavel in no.variaveis:
            self.visitar(variavel)

    def visitar_EscreverNode(self, no):
        for expressao in no.expressoes:
            self.visitar(expressao)

    def visitar_StringNode(self, no):
        return "string"

    def visitar_ExprNode(self, no):
        return self.visitar(no.termo)

    def visitar_TermoNode(self, no):
        return self.visitar(no.fator)