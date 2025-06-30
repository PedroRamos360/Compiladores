from abstract_syntax_tree import *
from tabela_de_simbolos import TabelaDeSimbolos, Simbolo


class SemanticError(Exception):
    def __init__(self, mensagem, token=None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.token = token

    def __str__(self):
        if self.token:
            return f"Erro Semântico: {self.mensagem} na linha {self.token.linha}, coluna {self.token.coluna}"
        return f"Erro Semântico: {self.mensagem}"


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
        if no.declaracoes:
            if isinstance(no.declaracoes, DeclaracoesNode):
                self.visitar(no.declaracoes)
            else:
                for declaracao in no.declaracoes:
                    self.visitar(declaracao)
        self.visitar(no.bloco)

    def visitar_DeclaracoesNode(self, no):
        """Visita o nó de declarações"""
        if hasattr(no, "declaracoes") and no.declaracoes:
            for declaracao in no.declaracoes:
                self.visitar(declaracao)

    def visitar_BlocoNode(self, no):
        if hasattr(no, "lista_comandos") and no.lista_comandos:
            if isinstance(no.lista_comandos, ListaComandosNode):
                self.visitar(no.lista_comandos)
            else:
                for comando in no.lista_comandos:
                    self.visitar(comando)

    def visitar_ListaComandosNode(self, no):
        """Visita uma lista de comandos"""
        if hasattr(no, "comandos") and no.comandos:
            for comando in no.comandos:
                self.visitar(comando)

    def visitar_CompostoNode(self, no):
        """Visita um comando composto"""
        if hasattr(no, "lista_comandos") and no.lista_comandos:
            if isinstance(no.lista_comandos, list):
                for comando in no.lista_comandos:
                    self.visitar(comando)
            else:
                self.visitar(no.lista_comandos)

    def visitar_DeclaracaoVarNode(self, no):
        nome_tipo = no.tipo_node.valor
        for no_var in no.var_nodes:
            nome_variavel = no_var.valor
            if self.tabela_de_simbolos.buscar(nome_variavel):
                raise SemanticError(
                    f"Variável '{nome_variavel}' já declarada.", token=no_var.token
                )
            simbolo = Simbolo(nome_variavel, nome_tipo)
            self.tabela_de_simbolos.definir(simbolo)

    def visitar_AtribuicaoNode(self, no):
        no_variavel = no.esquerda
        simbolo = self.tabela_de_simbolos.buscar(no_variavel.valor)
        if not simbolo:
            raise SemanticError(
                f"Variável '{no_variavel.valor}' não declarada.",
                token=no_variavel.token,
            )

        tipo_expressao = self.visitar(no.direita)

        if simbolo.tipo != tipo_expressao:
            raise SemanticError(
                f"Incompatibilidade de tipos. Não é possível atribuir '{tipo_expressao}' para a variável '{no_variavel.valor}' do tipo '{simbolo.tipo}'.",
                token=no.op,
            )

    def extrair_token_de_no(self, no):
        if hasattr(no, "token") and no.token:
            return no.token

        if hasattr(no, "valor") and hasattr(no, "token"):
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

    def visitar_SeNode(self, no):
        """Visita um comando SE"""
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

    def visitar_EnquantoNode(self, no):
        """Visita um comando ENQUANTO"""
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

    def visitar_LerNode(self, no):
        """Visita um comando LER"""
        if hasattr(no, "variaveis") and no.variaveis:
            for variavel in no.variaveis:
                simbolo = self.tabela_de_simbolos.buscar(variavel.valor)
                if not simbolo:
                    raise SemanticError(
                        f"Variável '{variavel.valor}' não declarada.",
                        token=variavel.token,
                    )

    def visitar_EscreverNode(self, no):
        """Visita um comando ESCREVER"""
        if hasattr(no, "expressoes") and no.expressoes:
            for expr in no.expressoes:
                self.visitar(expr)

    def visitar_StringVarNode(self, no):
        """Visita um StringVar"""
        if hasattr(no, "tipo") and no.tipo == "expr":
            if hasattr(no, "expr") and no.expr:
                return self.visitar(no.expr)
        return "string"

    def visitar_ExprNode(self, no):
        """Visita uma expressão"""
        if hasattr(no, "termo") and no.termo:
            tipo_termo = self.visitar(no.termo)
            if hasattr(no, "expr2") and no.expr2:
                self.visitar(no.expr2)
            return tipo_termo
        return "inteiro"

    def visitar_TermoNode(self, no):
        """Visita um termo"""
        if hasattr(no, "fator") and no.fator:
            tipo_fator = self.visitar(no.fator)
            if hasattr(no, "termo2") and no.termo2:
                self.visitar(no.termo2)
            return tipo_fator
        return "inteiro"

    def visitar_FatorNode(self, no):
        """Visita um fator"""
        if hasattr(no, "tipo"):
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
                return "inteiro"
        return "inteiro"

    def visitar_Expr2Node(self, no):
        """Visita continuação de expressão"""
        if hasattr(no, "operador") and no.operador:
            if hasattr(no, "termo") and no.termo:
                tipo_termo = self.visitar(no.termo)
            if hasattr(no, "expr2") and no.expr2:
                self.visitar(no.expr2)
            return "inteiro"
        return "inteiro"

    def visitar_Termo2Node(self, no):
        """Visita continuação de termo"""
        if hasattr(no, "operador") and no.operador:
            if hasattr(no, "fator") and no.fator:
                tipo_fator = self.visitar(no.fator)
            if hasattr(no, "termo2") and no.termo2:
                self.visitar(no.termo2)
            return "inteiro"
        return "inteiro"

    def visitar_IdNode(self, no):
        """Visita um identificador"""
        if hasattr(no, "valor"):
            simbolo = self.tabela_de_simbolos.buscar(no.valor)
            if not simbolo:
                raise SemanticError(
                    f"Variável '{no.valor}' não declarada.",
                    token=no.token if hasattr(no, "token") else None,
                )
            return simbolo.tipo
        return "inteiro"

    def visitar_ExprLogicoSimpleNode(self, no):
        """Visita expressão lógica simples"""
        if hasattr(no, "id_node") and no.id_node:
            return self.visitar(no.id_node)
        return "lógico"

    def visitar_ExprLogicoNode(self, no):
        """Visita uma expressão lógica"""
        if no.esquerda and no.direita:
            tipo_esquerda = self.visitar(no.esquerda)
            tipo_direita = self.visitar(no.direita)
            if tipo_esquerda != tipo_direita:
                raise SemanticError(
                    f"Incompatibilidade de tipos em expressão lógica: {tipo_esquerda} e {tipo_direita}"
                )
            return "lógico"
        return "lógico"

    def visitar_OpLogicoNode(self, no):
        """Visita operador lógico (nada a fazer)"""
        pass

    def visitar_NumeroNode(self, no):
        """Visita um número"""
        return "inteiro"

    def visitar_StringNode(self, no):
        """Visita uma string"""
        return "string"

    def visitar_VariavelNode(self, no):
        """Visita uma variável"""
        simbolo = self.tabela_de_simbolos.buscar(no.valor)
        if not simbolo:
            raise SemanticError(f"Variável '{no.valor}' não declarada.", token=no.token)
        return simbolo.tipo

    def visitar_OpBinariaNode(self, no):
        """Visita operação binária"""
        if no.esquerda and no.direita:
            tipo_esquerda = self.visitar(no.esquerda)
            tipo_direita = self.visitar(no.direita)
            if tipo_esquerda != tipo_direita:
                raise SemanticError(
                    f"Incompatibilidade de tipos em operação binária: {tipo_esquerda} e {tipo_direita}"
                )
            return tipo_esquerda
        return "inteiro"

    def visitar_OpUnariaNode(self, no):
        """Visita operação unária"""
        if no.expr:
            return self.visitar(no.expr)
        return "inteiro"

    def visitar_TipoNode(self, no):
        """Visita um tipo (nada a fazer)"""
        pass
