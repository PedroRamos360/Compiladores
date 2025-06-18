class ASTNode:
    """Nó base para todos os nós da AST."""

    pass


class ProgramaNode(ASTNode):
    def __init__(self, nome, declaracoes, bloco):
        self.nome = nome
        self.declaracoes = declaracoes
        self.bloco = bloco


class BlocoNode(ASTNode):
    def __init__(self, lista_comandos):
        self.lista_comandos = lista_comandos


class DeclaracaoVarNode(ASTNode):
    def __init__(self, var_nodes, tipo_node):
        self.var_nodes = var_nodes
        self.tipo_node = tipo_node


class VariavelNode(ASTNode):
    def __init__(self, token):
        self.token = token
        self.valor = token.valor


class TipoNode(ASTNode):
    def __init__(self, token):
        self.token = token
        self.valor = token.valor


class AtribuicaoNode(ASTNode):
    def __init__(self, esquerda, op, direita):
        self.esquerda = esquerda
        self.op = op
        self.direita = direita


class SeNode(ASTNode):
    def __init__(self, condicao, ramo_entao, ramo_senao=None):
        self.condicao = condicao
        self.ramo_entao = ramo_entao
        self.ramo_senao = ramo_senao


class EnquantoNode(ASTNode):
    def __init__(self, condicao, corpo):
        self.condicao = condicao
        self.corpo = corpo


class EscreverNode(ASTNode):
    def __init__(self, expressoes):
        self.expressoes = expressoes


class LerNode(ASTNode):
    def __init__(self, variaveis):
        self.variaveis = variaveis


class OpBinariaNode(ASTNode):
    def __init__(self, esquerda, op, direita):
        self.esquerda = esquerda
        self.op = op
        self.direita = direita


class OpUnariaNode(ASTNode):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr


class NumeroNode(ASTNode):
    def __init__(self, token):
        self.token = token
        self.valor = int(token.valor)


class StringNode(ASTNode):
    def __init__(self, token):
        self.token = token
        self.valor = token.valor[1:-1]  # Remove as aspas


class ExprNode(ASTNode):
    def __init__(self, termo, expr2):
        self.termo = termo
        self.expr2 = expr2


class TermoNode(ASTNode):
    def __init__(self, fator, termo2):
        self.fator = fator
        self.termo2 = termo2


class ExprLogicoNode(ASTNode):
    def __init__(self, esquerda, operador, direita):
        self.esquerda = esquerda
        self.operador = operador
        self.direita = direita
