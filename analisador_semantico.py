from typing import Optional
from abstract_syntax_tree import *
from tabela_de_simbolos import TabelaDeSimbolos, Simbolo


class SemanticError(Exception):
    def __init__(self, mensagem: str, token: Optional[Token] = None) -> None:
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.token = token

    def __str__(self) -> str:
        if self.token:
            return f"Erro Semântico: {self.mensagem} na linha {self.token.linha}, coluna {self.token.coluna}"
        return f"Erro Semântico: {self.mensagem}"


class AnalisadorSemantico:
    def __init__(self) -> None:
        self.tabela_de_simbolos = TabelaDeSimbolos()

    def visitar(self, no: ASTNode) -> Optional[str]:
        nome_metodo = f"visitar_{type(no).__name__}"
        visitante = getattr(self, nome_metodo, self.visitante_generico)
        return visitante(no)

    def visitante_generico(self, no: ASTNode) -> None:
        raise Exception(f"Nenhum método visitar_{type(no).__name__} definido")

    def visitar_ProgramaNode(self, no: ProgramaNode) -> None:
        if no.declaracoes:
            self.visitar(no.declaracoes)
        self.visitar(no.bloco)

    def visitar_DeclaracoesNode(self, no: DeclaracoesNode) -> None:
        if hasattr(no, "declaracoes") and no.declaracoes:
            for declaracao in no.declaracoes:
                self.visitar(declaracao)

    def visitar_BlocoNode(self, no: BlocoNode) -> None:
        if hasattr(no, "lista_comandos") and no.lista_comandos:
            for comando in no.lista_comandos:
                self.visitar(comando)

    def visitar_DeclaracaoVarNode(self, no: DeclaracaoVarNode) -> None:
        nome_tipo = no.tipo_node.valor
        for no_var in no.var_nodes:
            nome_variavel = no_var.valor
            if self.tabela_de_simbolos.buscar(nome_variavel):
                raise SemanticError(
                    f"Variável '{nome_variavel}' já declarada.", token=no_var.token
                )
            simbolo = Simbolo(nome_variavel, nome_tipo)
            self.tabela_de_simbolos.definir(simbolo)

    def visitar_AtribuicaoNode(self, no: AtribuicaoNode) -> None:
        no_variavel = no.esquerda
        simbolo = self.tabela_de_simbolos.buscar(no_variavel.valor)
        if not simbolo:
            raise SemanticError(
                f"Variável '{no_variavel.valor}' não declarada.",
                token=no_variavel.token,
            )
        tipo_expressao = self.visitar(no.direita)
        if simbolo.tipo == "lógico" and tipo_expressao == "inteiro":
            raise SemanticError(
                f"Incompatibilidade de tipos. Não é possível atribuir '{tipo_expressao}' para a variável '{no_variavel.valor}' do tipo '{simbolo.tipo}'.",
                token=no.op,
            )

    def extrair_token_de_no(self, no: ASTNode) -> Optional[Token]:
        if hasattr(no, "token") and no.token:
            return no.token
        elif hasattr(no, "esquerda") and hasattr(no.esquerda, "token"):
            return no.esquerda.token
        elif hasattr(no, "id_node") and hasattr(no.id_node, "token"):
            return no.id_node.token
        elif hasattr(no, "termo") and hasattr(no.termo, "token"):
            return no.termo.token
        elif hasattr(no, "fator") and hasattr(no.fator, "token"):
            return no.fator.token

        return None

    def visitar_SeNode(self, no: SeNode) -> None:
        if no.condicao:
            tipo_condicao = self.visitar(no.condicao)
            if tipo_condicao != "lógico":
                token_erro = self.extrair_token_de_no(no.condicao)
                raise SemanticError(
                    f"Condição em 'se' deve ser do tipo lógico, mas encontrado '{tipo_condicao}'.",
                    token=token_erro,
                )

        if no.ramo_entao:
            self.visitar(no.ramo_entao)

        if hasattr(no, "ramo_senao") and no.ramo_senao:
            self.visitar(no.ramo_senao)

    def visitar_EnquantoNode(self, no: EnquantoNode) -> None:
        if no.condicao:
            tipo_condicao = self.visitar(no.condicao)
            if tipo_condicao != "lógico":
                token_erro = self.extrair_token_de_no(no.condicao)
                raise SemanticError(
                    f"Condição em 'enquanto' deve ser do tipo lógico, mas encontrado '{tipo_condicao}'.",
                    token=token_erro,
                )

        if no.corpo:
            self.visitar(no.corpo)

    def visitar_LerNode(self, no: LerNode) -> None:
        if hasattr(no, "variaveis") and no.variaveis:
            for variavel in no.variaveis:
                simbolo = self.tabela_de_simbolos.buscar(variavel.valor)
                if not simbolo:
                    raise SemanticError(
                        f"Variável '{variavel.valor}' não declarada.",
                        token=variavel.token,
                    )

    def visitar_EscreverNode(self, no: EscreverNode) -> None:
        if hasattr(no, "expressoes") and no.expressoes:
            for expr in no.expressoes:
                self.visitar(expr)

    def visitar_StringVarNode(self, no: StringVarNode) -> str:
        if hasattr(no, "tipo") and no.tipo == "expr":
            if hasattr(no, "expr") and no.expr:
                return self.visitar(no.expr)
        return "string"

    def visitar_ExprNode(self, no: ExprNode) -> str:
        if hasattr(no, "termo") and no.termo:
            tipo_termo = self.visitar(no.termo)
            if hasattr(no, "expr2") and no.expr2:
                tipo_expr2 = self.visitar(no.expr2)
            return self.juncao_tipos(tipo_termo, tipo_expr2)
        return "inteiro"

    def visitar_TermoNode(self, no: TermoNode) -> str:
        tipo_fator = self.visitar(no.fator)
        if hasattr(no, "termo2") and no.termo2:
            tipo_termo2 = self.visitar(no.termo2)
        return self.juncao_tipos(tipo_fator, tipo_termo2)

    def visitar_FatorNode(self, no: FatorNode) -> str:
        if no.tipo == "parenteses" and hasattr(no, "expr") and no.expr:
            return self.visitar(no.expr)
        elif no.tipo == "negativo" and hasattr(no, "fator") and no.fator:
            return self.visitar(no.fator)
        elif no.tipo == "id" and hasattr(no, "valor"):
            simbolo = self.tabela_de_simbolos.buscar(no.valor)
            if not simbolo:
                raise SemanticError(
                    f"Variável '{no.valor}' não declarada.",
                    token=no.token if hasattr(no, "token") else None,
                )
            return simbolo.tipo
        elif no.tipo == "num":
            return self.verificar_tipo_numero(no.valor)

    def visitar_Expr2Node(self, no: Expr2Node) -> str:
        if hasattr(no, "operador") and no.operador:
            if hasattr(no, "termo") and no.termo:
                tipo_termo = self.visitar(no.termo)
            if hasattr(no, "expr2") and no.expr2:
                tipo_expr2 = self.visitar(no.expr2)
            return self.juncao_tipos(tipo_termo, tipo_expr2)
        return "lógico"

    def visitar_Termo2Node(self, no: Termo2Node) -> str:
        if hasattr(no, "operador") and no.operador:
            if hasattr(no, "fator") and no.fator:
                tipo_fator = self.visitar(no.fator)
            if hasattr(no, "termo2") and no.termo2:
                tipo_termo2 = self.visitar(no.termo2)
            return self.juncao_tipos(tipo_fator, tipo_termo2)
        return "lógico"

    def visitar_IdNode(self, no: IdNode) -> str:
        if hasattr(no, "valor"):
            simbolo = self.tabela_de_simbolos.buscar(no.valor)
            if not simbolo:
                raise SemanticError(
                    f"Variável '{no.valor}' não declarada.",
                    token=no.token if hasattr(no, "token") else None,
                )
            return simbolo.tipo
        return "inteiro"

    def visitar_ExprLogicoSimpleNode(self, no: ExprLogicoSimpleNode) -> str:
        if hasattr(no, "id_node") and no.id_node:
            return self.visitar(no.id_node)
        return "lógico"

    def visitar_ExprLogicoNode(self, no: ExprLogicoNode) -> str:
        return "lógico"

    def visitar_NumeroNode(self, no: NumeroNode) -> str:
        return self.verificar_tipo_numero(no.valor)

    def visitar_StringNode(self, no: StringNode) -> str:
        return "string"

    def visitar_VariavelNode(self, no: VariavelNode) -> str:
        simbolo = self.tabela_de_simbolos.buscar(no.valor)
        if not simbolo:
            raise SemanticError(f"Variável '{no.valor}' não declarada.", token=no.token)
        return simbolo.tipo

    def visitar_OpBinariaNode(self, no: OpBinariaNode) -> str:
        if no.esquerda and no.direita:
            tipo_esquerda = self.visitar(no.esquerda)
            tipo_direita = self.visitar(no.direita)
            if tipo_esquerda != tipo_direita:
                raise SemanticError(
                    f"Incompatibilidade de tipos em operação binária: {tipo_esquerda} e {tipo_direita}"
                )
            return tipo_esquerda
        return "inteiro"

    def visitar_OpUnariaNode(self, no: OpUnariaNode) -> str:
        if no.expr:
            return self.visitar(no.expr)
        return "inteiro"


    def verificar_tipo_numero(self, numero: int) -> str:
        if numero == 0 or numero == 1:
            return "lógico"
        return "inteiro"

    def juncao_tipos(self, tipo1: str, tipo2: str) -> str:
        if tipo1 == "lógico" and tipo2 == "lógico":
            return "lógico"
        return "inteiro"
