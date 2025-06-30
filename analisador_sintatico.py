from abstract_syntax_tree import *
from analisador_lexico import Token


class AnalisadorSintatico:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.posicao = 0

    def _token_atual(self):
        return self.tokens[self.posicao]

    def _avancar(self):
        self.posicao += 1

    def _consumir(self, tipo_esperado):
        token = self._token_atual()
        if token.tipo == tipo_esperado:
            self._avancar()
            return token
        else:
            raise SyntaxError(
                f"Erro de sintaxe: Esperado token '{tipo_esperado}', mas encontrou '{token.tipo}' "
                f"na linha {token.linha}, coluna {token.coluna}."
            )

    def analisar(self) -> ProgramaNode:
        return self._programa()

    def _programa(self):
        """<prog>::=programa id; [<declarações>] <bloco> ."""
        self._consumir("PROGRAMA")
        nome_programa = self._consumir("ID").valor
        self._consumir("PONTO_VÍRGULA")

        declaracoes = self._declaracoes()
        bloco = self._bloco()

        self._consumir("PONTO")
        return ProgramaNode(nome_programa, declaracoes, bloco)

    def _declaracoes(self):
        """[<declarações>] ::= var ..."""
        declaracoes = []
        if self._token_atual().tipo == "VAR":
            self._consumir("VAR")
            while self._token_atual().tipo == "ID":
                declaracoes.append(self._lista_declaracao_var())
        return DeclaracoesNode(declaracoes) if declaracoes else None

    def _lista_declaracao_var(self):
        """id {,id} : <tipo>;"""
        vars_nos = [VariavelNode(self._consumir("ID"))]
        while self._token_atual().tipo == "VÍRGULA":
            self._consumir("VÍRGULA")
            vars_nos.append(VariavelNode(self._consumir("ID")))

        self._consumir("DOIS_PONTOS")
        tipo_no = self._tipo()
        self._consumir("PONTO_VÍRGULA")
        return DeclaracaoVarNode(vars_nos, tipo_no)

    def _tipo(self):
        """<tipo> ::= inteiro | lógico"""
        token = self._token_atual()
        if token.tipo == "INTEIRO":
            self._consumir("INTEIRO")
            return TipoNode(token)
        elif token.tipo == "LÓGICO":
            self._consumir("LÓGICO")
            return TipoNode(token)
        else:
            raise SyntaxError(
                f"Tipo desconhecido '{token.valor}' na linha {token.linha}"
            )

    def _bloco(self):
        """<bloco> ::= início <lista comandos> fim"""
        self._consumir("INÍCIO")
        lista_comandos = self._lista_comandos()
        self._consumir("FIM")
        return BlocoNode(lista_comandos.comandos)

    def _lista_comandos(self):
        """<lista comandos> ::= <comando>; {<comando>;}"""
        comandos = [self._comando()]
        while self._token_atual().tipo == "PONTO_VÍRGULA":
            self._consumir("PONTO_VÍRGULA")
            if self._token_atual().tipo == "FIM":
                break
            comandos.append(self._comando())
        return ListaComandosNode(comandos)

    def _comando(self):
        """<comando> ::= <atribuição> | <leitura> | <escrita> | <composto> | <condicional> | <repetição>"""
        token_tipo = self._token_atual().tipo
        if token_tipo == "ID":
            return self._atribuicao()
        elif token_tipo == "LER":
            return self._leitura()
        elif token_tipo == "ESCREVER":
            return self._escrita()
        elif token_tipo == "INÍCIO":
            return self._bloco()
        elif token_tipo == "SE":
            return self._condicional()
        elif token_tipo == "ENQUANTO":
            return self._repeticao()
        else:
            token_atual = self._token_atual()
            raise SyntaxError(
                f"Comando inesperado '{token_atual.valor}' na linha {token_atual.linha}"
            )

    def _atribuicao(self) -> AtribuicaoNode:
        """<atribuição> ::= id := <expr>"""
        esquerda = VariavelNode(self._consumir("ID"))
        op = self._consumir("ATRIBUIÇÃO")
        direita = self._expr()
        return AtribuicaoNode(esquerda, op, direita)

    def _leitura(self):
        """<leitura> ::= ler (id {,id})"""
        self._consumir("LER")
        self._consumir("LPAREN")
        variaveis = [VariavelNode(self._consumir("ID"))]
        while self._token_atual().tipo == "VÍRGULA":
            self._consumir("VÍRGULA")
            variaveis.append(VariavelNode(self._consumir("ID")))
        self._consumir("RPAREN")
        return LerNode(variaveis)

    def _escrita(self):
        """<escrita> ::= escrever (<stringvar> {,<stringvar>})"""
        self._consumir("ESCREVER")
        self._consumir("LPAREN")
        expressoes = [self._stringvar()]
        while self._token_atual().tipo == "VÍRGULA":
            self._consumir("VÍRGULA")
            expressoes.append(self._stringvar())
        self._consumir("RPAREN")
        return EscreverNode(expressoes)

    def _stringvar(self):
        """<stringvar> ::= str | <expr>"""
        if self._token_atual().tipo == "STRING":
            token = self._consumir("STRING")
            return StringVarNode("string", valor=token.valor[1:-1])
        else:
            expr = self._expr()
            return StringVarNode("expr", expr=expr)

    def _condicional(self):
        """<condicional> ::= se <exprLogico> então <comando> [senão <comando>]"""
        self._consumir("SE")
        condicao = self._exprLogico()
        self._consumir("ENTÃO")
        ramo_entao = self._comando()
        ramo_senao = None
        if self._token_atual().tipo == "SENÃO":
            self._consumir("SENÃO")
            ramo_senao = self._comando()
        return SeNode(condicao, ramo_entao, ramo_senao)

    def _repeticao(self):
        """<repetição> ::= enquanto <exprLogico> faça <comando>"""
        self._consumir("ENQUANTO")
        condicao = self._exprLogico()
        self._consumir("FAÇA")
        corpo = self._comando()
        return EnquantoNode(condicao, corpo)

    def _expr(self):
        """<expr> ::= <termo> <expr2>"""
        termo = self._termo()
        expr2 = self._expr2()
        return ExprNode(termo, expr2)

    def _termo(self):
        """<termo> ::= <fator> <termo2>"""
        fator = self._fator()
        termo2 = self._termo2()
        return TermoNode(fator, termo2)

    def _termo2(self):
        """<termo2> ::= * <fator> <termo2> | / <fator> <termo2> | ε"""
        if self._token_atual().tipo == "MULT":
            op = self._consumir("MULT")
            fator = self._fator()
            termo2 = self._termo2()
            return Termo2Node(op, fator, termo2)
        elif self._token_atual().tipo == "DIV":
            op = self._consumir("DIV")
            fator = self._fator()
            termo2 = self._termo2()
            return Termo2Node(op, fator, termo2)
        else:
            return Termo2Node()

    def _expr2(self):
        """<expr2> ::= + <termo> <expr2> | - <termo> <expr2> | ε"""
        if self._token_atual().tipo == "MAIS":
            op = self._consumir("MAIS")
            termo = self._termo()
            expr2 = self._expr2()
            return Expr2Node(op, termo, expr2)
        elif self._token_atual().tipo == "MENOS":
            op = self._consumir("MENOS")
            termo = self._termo()
            expr2 = self._expr2()
            return Expr2Node(op, termo, expr2)
        else:
            return Expr2Node()

    def _fator(self):
        """<fator> ::= (<expr>) | - <fator> | id | num"""
        if self._token_atual().tipo == "LPAREN":
            self._consumir("LPAREN")
            expr = self._expr()
            self._consumir("RPAREN")
            return FatorNode("parenteses", expr=expr)
        elif self._token_atual().tipo == "MENOS":
            op = self._consumir("MENOS")
            fator = self._fator()
            return FatorNode("negativo", fator=fator, token=op)
        elif self._token_atual().tipo == "ID":
            token = self._consumir("ID")
            return FatorNode("id", valor=token.valor, token=token)
        elif self._token_atual().tipo == "NÚMERO":
            token = self._consumir("NÚMERO")
            return FatorNode("num", valor=int(token.valor), token=token)
        else:
            raise SyntaxError(
                f"Fator inesperado '{self._token_atual().valor}' na linha {self._token_atual().linha}"
            )

    def _exprLogico(self):
        """<exprLogico> ::= <expr> <opLogico> <expr> | id"""
        if self._token_atual().tipo == "ID":
            if self.posicao + 1 < len(self.tokens):
                proximo_token = self.tokens[self.posicao + 1]
                if proximo_token.tipo not in {
                    "MENOR",
                    "MENOR_IGUAL",
                    "MAIOR",
                    "MAIOR_IGUAL",
                    "IGUAL",
                    "DIFERENTE",
                }:
                    token_id = self._consumir("ID")
                    return ExprLogicoSimpleNode(IdNode(token_id))

        node_esquerda = self._expr()
        op_token = self._opLogico()
        node_direita = self._expr()
        return ExprLogicoNode(node_esquerda, op_token, node_direita)

    def _opLogico(self):
        """<opLogico> ::= < | <= | > | >= | = | <>"""
        token = self._token_atual()
        if token.tipo in {
            "MENOR",
            "MENOR_IGUAL",
            "MAIOR",
            "MAIOR_IGUAL",
            "IGUAL",
            "DIFERENTE",
        }:
            self._avancar()
            return OpLogicoNode(token)
        else:
            raise SyntaxError(
                f"Operador lógico inesperado '{token.valor}' na linha {token.linha}"
            )
