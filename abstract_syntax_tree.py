class ASTNode:
    """Nó base para todos os nós da AST."""
    
    def __str__(self):
        return f"{self.__class__.__name__}()"
    
    def __repr__(self):
        return self.__str__()


class ProgramaNode(ASTNode):
    def __init__(self, nome, declaracoes, bloco):
        self.nome = nome
        self.declaracoes = declaracoes
        self.bloco = bloco
    
    def __str__(self):
        return f"ProgramaNode(nome='{self.nome}', declaracoes={len(self.declaracoes) if self.declaracoes else 0}, bloco={bool(self.bloco)})"


class BlocoNode(ASTNode):
    def __init__(self, lista_comandos):
        self.lista_comandos = lista_comandos
    
    def __str__(self):
        return f"BlocoNode(comandos={len(self.lista_comandos) if self.lista_comandos else 0})"


class DeclaracaoVarNode(ASTNode):
    def __init__(self, var_nodes, tipo_node):
        self.var_nodes = var_nodes
        self.tipo_node = tipo_node
    
    def __str__(self):
        vars_names = [var.valor for var in self.var_nodes if hasattr(var, 'valor')] if self.var_nodes else []
        tipo = self.tipo_node.valor if self.tipo_node and hasattr(self.tipo_node, 'valor') else 'None'
        return f"DeclaracaoVarNode(vars={vars_names}, tipo='{tipo}')"


class VariavelNode(ASTNode):
    def __init__(self, token):
        self.token = token
        self.valor = token.valor
    
    def __str__(self):
        return f"VariavelNode('{self.valor}')"


class TipoNode(ASTNode):
    def __init__(self, token):
        self.token = token
        self.valor = token.valor
    
    def __str__(self):
        return f"TipoNode('{self.valor}')"


class AtribuicaoNode(ASTNode):
    def __init__(self, esquerda, op, direita):
        self.esquerda = esquerda
        self.op = op
        self.direita = direita
    
    def __str__(self):
        var_nome = self.esquerda.valor if hasattr(self.esquerda, 'valor') else str(self.esquerda)
        op_valor = self.op.valor if hasattr(self.op, 'valor') else str(self.op)
        return f"AtribuicaoNode('{var_nome}' {op_valor} {type(self.direita).__name__})"


class SeNode(ASTNode):
    def __init__(self, condicao, ramo_entao, ramo_senao=None):
        self.condicao = condicao
        self.ramo_entao = ramo_entao
        self.ramo_senao = ramo_senao
    
    def __str__(self):
        return f"SeNode(condicao={type(self.condicao).__name__}, entao={type(self.ramo_entao).__name__}, senao={type(self.ramo_senao).__name__ if self.ramo_senao else None})"


class EnquantoNode(ASTNode):
    def __init__(self, condicao, corpo):
        self.condicao = condicao
        self.corpo = corpo
    
    def __str__(self):
        return f"EnquantoNode(condicao={type(self.condicao).__name__}, corpo={type(self.corpo).__name__})"


class EscreverNode(ASTNode):
    def __init__(self, expressoes):
        self.expressoes = expressoes
    
    def __str__(self):
        tipos_expr = [type(expr).__name__ for expr in self.expressoes] if self.expressoes else []
        return f"EscreverNode(expressoes={tipos_expr})"


class LerNode(ASTNode):
    def __init__(self, variaveis):
        self.variaveis = variaveis
    
    def __str__(self):
        vars_names = [var.valor for var in self.variaveis if hasattr(var, 'valor')] if self.variaveis else []
        return f"LerNode(vars={vars_names})"


class OpBinariaNode(ASTNode):
    def __init__(self, esquerda, op, direita):
        self.esquerda = esquerda
        self.op = op
        self.direita = direita
    
    def __str__(self):
        op_valor = self.op.valor if hasattr(self.op, 'valor') else str(self.op)
        esq_tipo = type(self.esquerda).__name__ if self.esquerda else 'None'
        dir_tipo = type(self.direita).__name__ if self.direita else 'None'
        return f"OpBinariaNode({esq_tipo} {op_valor} {dir_tipo})"


class OpUnariaNode(ASTNode):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr
    
    def __str__(self):
        op_valor = self.op.valor if hasattr(self.op, 'valor') else str(self.op)
        expr_tipo = type(self.expr).__name__ if self.expr else 'None'
        return f"OpUnariaNode({op_valor}{expr_tipo})"


class NumeroNode(ASTNode):
    def __init__(self, token):
        self.token = token
        self.valor = int(token.valor)
    
    def __str__(self):
        return f"NumeroNode({self.valor})"


class StringNode(ASTNode):
    def __init__(self, token):
        self.token = token
        self.valor = token.valor[1:-1] 
    
    def __str__(self):
        return f"StringNode('{self.valor}')"


class ExprNode(ASTNode):
    def __init__(self, termo, expr2):
        self.termo = termo
        self.expr2 = expr2
    
    def __str__(self):
        termo_tipo = type(self.termo).__name__ if self.termo else 'None'
        expr2_tipo = type(self.expr2).__name__ if self.expr2 else 'None'
        return f"ExprNode(termo={termo_tipo}, expr2={expr2_tipo})"


class TermoNode(ASTNode):
    def __init__(self, fator, termo2):
        self.fator = fator
        self.termo2 = termo2
    
    def __str__(self):
        fator_tipo = type(self.fator).__name__ if self.fator else 'None'
        termo2_tipo = type(self.termo2).__name__ if self.termo2 else 'None'
        return f"TermoNode(fator={fator_tipo}, termo2={termo2_tipo})"


class ExprLogicoNode(ASTNode):
    def __init__(self, esquerda, operador, direita):
        self.esquerda = esquerda
        self.operador = operador
        self.direita = direita
    
    def __str__(self):
        op_valor = self.operador.valor if hasattr(self.operador, 'valor') else str(self.operador)
        esq_tipo = type(self.esquerda).__name__ if self.esquerda else 'None'
        dir_tipo = type(self.direita).__name__ if self.direita else 'None'
        return f"ExprLogicoNode({esq_tipo} {op_valor} {dir_tipo})"