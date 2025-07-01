from typing import Optional, List, Union
from analisador_lexico import Token


class ASTNode:
    """Nó base para todos os nós da AST."""

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __repr__(self) -> str:
        return self.__str__()


class ProgramaNode(ASTNode):
    def __init__(
        self, nome: str, declaracoes: Optional["DeclaracoesNode"], bloco: "BlocoNode"
    ) -> None:
        self.nome = nome
        self.declaracoes = declaracoes
        self.bloco = bloco

    def __str__(self) -> str:
        declaracoes_count = 0
        if self.declaracoes:
            if hasattr(self.declaracoes, "declaracoes"):
                declaracoes_count = (
                    len(self.declaracoes.declaracoes)
                    if self.declaracoes.declaracoes
                    else 0
                )
            elif isinstance(self.declaracoes, list):
                declaracoes_count = len(self.declaracoes)
            else:
                declaracoes_count = 1
        return f"ProgramaNode(nome='{self.nome}', declaracoes={declaracoes_count}, bloco={bool(self.bloco)})"


class BlocoNode(ASTNode):
    def __init__(self, lista_comandos: List["ComandoNode"]) -> None:
        self.lista_comandos = lista_comandos

    def __str__(self) -> str:
        return f"BlocoNode(comandos={len(self.lista_comandos) if self.lista_comandos else 0})"


class DeclaracaoVarNode(ASTNode):
    def __init__(self, var_nodes: List["VariavelNode"], tipo_node: "TipoNode") -> None:
        self.var_nodes = var_nodes
        self.tipo_node = tipo_node

    def __str__(self) -> str:
        vars_names = (
            [var.valor for var in self.var_nodes if hasattr(var, "valor")]
            if self.var_nodes
            else []
        )
        tipo = (
            self.tipo_node.valor
            if self.tipo_node and hasattr(self.tipo_node, "valor")
            else "None"
        )
        return f"DeclaracaoVarNode(vars={vars_names}, tipo='{tipo}')"


class VariavelNode(ASTNode):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.valor = token.valor

    def __str__(self) -> str:
        return f"VariavelNode('{self.valor}')"


class TipoNode(ASTNode):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.valor = token.valor

    def __str__(self) -> str:
        return f"TipoNode('{self.valor}')"


class ComandoNode(ASTNode):
    """Nó base para todos os tipos de comando"""

    pass


class AtribuicaoNode(ComandoNode):
    def __init__(self, esquerda: VariavelNode, op: Token, direita: "ExprNode") -> None:
        self.esquerda = esquerda
        self.op = op
        self.direita = direita

    def __str__(self) -> str:
        var_nome = (
            self.esquerda.valor
            if hasattr(self.esquerda, "valor")
            else str(self.esquerda)
        )
        op_valor = self.op.valor if hasattr(self.op, "valor") else str(self.op)
        return f"AtribuicaoNode('{var_nome}' {op_valor} {type(self.direita).__name__})"


class SeNode(ComandoNode):
    def __init__(
        self,
        condicao: "ExprLogicoNode",
        ramo_entao: ComandoNode,
        ramo_senao: Optional[ComandoNode] = None,
    ) -> None:
        self.condicao = condicao
        self.ramo_entao = ramo_entao
        self.ramo_senao = ramo_senao

    def __str__(self) -> str:
        return f"SeNode(condicao={type(self.condicao).__name__}, entao={type(self.ramo_entao).__name__}, senao={type(self.ramo_senao).__name__ if self.ramo_senao else None})"


class EnquantoNode(ComandoNode):
    def __init__(self, condicao: "ExprLogicoNode", corpo: ComandoNode) -> None:
        self.condicao = condicao
        self.corpo = corpo

    def __str__(self) -> str:
        return f"EnquantoNode(condicao={type(self.condicao).__name__}, corpo={type(self.corpo).__name__})"


class EscreverNode(ComandoNode):
    def __init__(self, expressoes: List["StringVarNode"]) -> None:
        self.expressoes = expressoes

    def __str__(self) -> str:
        tipos_expr = (
            [type(expr).__name__ for expr in self.expressoes] if self.expressoes else []
        )
        return f"EscreverNode(expressoes={tipos_expr})"


class LerNode(ComandoNode):
    def __init__(self, variaveis: List[VariavelNode]) -> None:
        self.variaveis = variaveis

    def __str__(self) -> str:
        vars_names = (
            [var.valor for var in self.variaveis if hasattr(var, "valor")]
            if self.variaveis
            else []
        )
        return f"LerNode(vars={vars_names})"


class OpBinariaNode(ASTNode):
    def __init__(self, esquerda: ASTNode, op: Token, direita: ASTNode) -> None:
        self.esquerda = esquerda
        self.op = op
        self.direita = direita

    def __str__(self) -> str:
        op_valor = self.op.valor if hasattr(self.op, "valor") else str(self.op)
        esq_tipo = type(self.esquerda).__name__ if self.esquerda else "None"
        dir_tipo = type(self.direita).__name__ if self.direita else "None"
        return f"OpBinariaNode({esq_tipo} {op_valor} {dir_tipo})"


class OpUnariaNode(ASTNode):
    def __init__(self, op: Token, expr: ASTNode) -> None:
        self.op = op
        self.expr = expr

    def __str__(self) -> str:
        op_valor = self.op.valor if hasattr(self.op, "valor") else str(self.op)
        expr_tipo = type(self.expr).__name__ if self.expr else "None"
        return f"OpUnariaNode({op_valor}{expr_tipo})"


class NumeroNode(ASTNode):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.valor = int(token.valor)

    def __str__(self) -> str:
        return f"NumeroNode({self.valor})"


class StringNode(ASTNode):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.valor = token.valor[1:-1]

    def __str__(self) -> str:
        return f"StringNode('{self.valor}')"


class ExprNode(ASTNode):
    def __init__(self, termo: "TermoNode", expr2: Optional["Expr2Node"]) -> None:
        self.termo = termo
        self.expr2 = expr2

    def __str__(self) -> str:
        termo_tipo = type(self.termo).__name__ if self.termo else "None"
        expr2_tipo = type(self.expr2).__name__ if self.expr2 else "None"
        return f"ExprNode(termo={termo_tipo}, expr2={expr2_tipo})"


class TermoNode(ASTNode):
    def __init__(self, fator: "FatorNode", termo2: Optional["Termo2Node"]) -> None:
        self.fator = fator
        self.termo2 = termo2

    def __str__(self) -> str:
        fator_tipo = type(self.fator).__name__ if self.fator else "None"
        termo2_tipo = type(self.termo2).__name__ if self.termo2 else "None"
        return f"TermoNode(fator={fator_tipo}, termo2={termo2_tipo})"


class ExprLogicoNode(ASTNode):
    def __init__(
        self, esquerda: ExprNode, operador: "OpLogicoNode", direita: ExprNode
    ) -> None:
        self.esquerda = esquerda
        self.operador = operador
        self.direita = direita

    def __str__(self) -> str:
        op_valor = (
            self.operador.valor
            if hasattr(self.operador, "valor")
            else str(self.operador)
        )
        esq_tipo = type(self.esquerda).__name__ if self.esquerda else "None"
        dir_tipo = type(self.direita).__name__ if self.direita else "None"
        return f"ExprLogicoNode({esq_tipo} {op_valor} {dir_tipo})"


class Expr2Node(ASTNode):
    """Representa a continuação de uma expressão: + <termo> <expr2> | - <termo> <expr2> | ε"""

    def __init__(
        self,
        operador: Optional[Token] = None,
        termo: Optional[TermoNode] = None,
        expr2: Optional["Expr2Node"] = None,
    ) -> None:
        self.operador = operador
        self.termo = termo
        self.expr2 = expr2

    def __str__(self) -> str:
        if self.operador is None:
            return "Expr2Node(ε)"
        op_valor = (
            self.operador.valor
            if hasattr(self.operador, "valor")
            else str(self.operador)
        )
        termo_tipo = type(self.termo).__name__ if self.termo else "None"
        expr2_tipo = type(self.expr2).__name__ if self.expr2 else "None"
        return f"Expr2Node({op_valor} {termo_tipo} {expr2_tipo})"


class Termo2Node(ASTNode):
    """Representa a continuação de um termo: * <fator> <termo2> | / <fator> <termo2> | ε"""

    def __init__(
        self,
        operador: Optional[Token] = None,
        fator: Optional["FatorNode"] = None,
        termo2: Optional["Termo2Node"] = None,
    ) -> None:
        self.operador = operador
        self.fator = fator
        self.termo2 = termo2

    def __str__(self) -> str:
        if self.operador is None:
            return "Termo2Node(ε)"
        op_valor = (
            self.operador.valor
            if hasattr(self.operador, "valor")
            else str(self.operador)
        )
        fator_tipo = type(self.fator).__name__ if self.fator else "None"
        termo2_tipo = type(self.termo2).__name__ if self.termo2 else "None"
        return f"Termo2Node({op_valor} {fator_tipo} {termo2_tipo})"


class FatorNode(ASTNode):
    def __init__(
        self,
        tipo: str,
        valor: Optional[Union[str, int]] = None,
        expr: Optional[ExprNode] = None,
        fator: Optional["FatorNode"] = None,
        token: Optional[Token] = None,
    ) -> None:
        self.tipo = tipo
        self.valor = valor
        self.expr = expr
        self.fator = fator
        self.token = token

    def __str__(self) -> str:
        if self.tipo == "parenteses":
            expr_tipo = type(self.expr).__name__ if self.expr else "None"
            return f"FatorNode(({expr_tipo}))"
        elif self.tipo == "negativo":
            fator_tipo = type(self.fator).__name__ if self.fator else "None"
            return f"FatorNode(-{fator_tipo})"
        elif self.tipo == "id":
            return f"FatorNode(id='{self.valor}')"
        elif self.tipo == "num":
            return f"FatorNode(num={self.valor})"
        else:
            return f"FatorNode(tipo='{self.tipo}')"


class OpLogicoNode(ASTNode):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.valor = token.valor

    def __str__(self) -> str:
        return f"OpLogicoNode('{self.valor}')"


class ExprLogicoSimpleNode(ASTNode):
    def __init__(self, id_node: "IdNode") -> None:
        self.id_node = id_node

    def __str__(self) -> str:
        id_valor = (
            self.id_node.valor if hasattr(self.id_node, "valor") else str(self.id_node)
        )
        return f"ExprLogicoSimpleNode(id='{id_valor}')"


class ListaComandosNode(ASTNode):
    def __init__(self, comandos: List[ComandoNode]) -> None:
        self.comandos = comandos

    def __str__(self) -> str:
        return f"ListaComandosNode(total={len(self.comandos) if self.comandos else 0})"


class StringVarNode(ASTNode):
    def __init__(
        self, tipo: str, valor: Optional[str] = None, expr: Optional[ExprNode] = None
    ) -> None:
        self.tipo = tipo
        self.valor = valor
        self.expr = expr

    def __str__(self) -> str:
        if self.tipo == "string":
            return f"StringVarNode(str='{self.valor}')"
        else:
            expr_tipo = type(self.expr).__name__ if self.expr else "None"
            return f"StringVarNode(expr={expr_tipo})"


class IdNode(ASTNode):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.valor = token.valor

    def __str__(self) -> str:
        return f"IdNode('{self.valor}')"


class DeclaracoesNode(ASTNode):
    def __init__(self, declaracoes: List[DeclaracaoVarNode]) -> None:
        self.declaracoes = declaracoes

    def __str__(self) -> str:
        return (
            f"DeclaracoesNode(total={len(self.declaracoes) if self.declaracoes else 0})"
        )
