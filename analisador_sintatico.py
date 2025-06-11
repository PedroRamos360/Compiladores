from abstract_syntax_tree import *


class AnalisadorSintatico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicao = 0

    def _token_atual(self):
        """Retorna o token atual sem avançar a posição."""
        return self.tokens[self.posicao]

    def _avancar(self):
        """Avança para o próximo token."""
        self.posicao += 1

    def _consumir(self, tipo_esperado):
        """Consome o token atual se for do tipo esperado, senão lança um erro."""
        token = self._token_atual()
        if token.tipo == tipo_esperado:
            self._avancar()
            return token
        else:
            raise SyntaxError(
                f"Erro de sintaxe: Esperado token '{tipo_esperado}', mas encontrou '{token.tipo}' "
                f"na linha {token.linha}, coluna {token.coluna}."
            )

    def analisar(self):
        """Ponto de entrada para iniciar a análise."""
        return self._programa()

    # --- MÉTODOS DE ANÁLISE PARA CADA REGRA DA GRAMÁTICA ---

    def _programa(self):
        """<prog> ::= programa id; [<declarações>] início <lista comandos> fim."""
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
        return declaracoes

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
        return BlocoNode(lista_comandos)

    def _lista_comandos(self):
        """<lista comandos> ::= <comando>; {<comando>;}"""
        comandos = [self._comando()]
        while self._token_atual().tipo == "PONTO_VÍRGULA":
            self._consumir("PONTO_VÍRGULA")
            # Permite ponto e vírgula final antes do 'fim'
            if self._token_atual().tipo == "FIM":
                break
            comandos.append(self._comando())
        return comandos

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
            return self._bloco()  # Comando composto
        elif token_tipo == "SE":
            return self._condicional()
        elif token_tipo == "ENQUANTO":
            return self._repeticao()
        else:
            token_atual = self._token_atual()
            raise SyntaxError(
                f"Comando inesperado '{token_atual.valor}' na linha {token_atual.linha}"
            )

    def _atribuicao(self):
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
            return StringNode(self._consumir("STRING"))
        else:
            return self._expr()

    def _condicional(self):
        """<condicional> ::= se <exprLogico> então <comando> [senão <comando>]"""
        self._consumir("SE")
        condicao = self._expr()
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
        condicao = self._expr()
        self._consumir("FAÇA")
        corpo = self._comando()
        return EnquantoNode(condicao, corpo)

    # --- MÉTODOS PARA ANÁLISE DE EXPRESSÕES (COM PRECEDÊNCIA) ---

    def _fator(self):
        """<fator> ::= (+|-) <fator> | NÚMERO | ( <expr> ) | ID"""
        token = self._token_atual()
        if token.tipo in ("MAIS", "MENOS"):
            op = self._consumir(token.tipo)
            return OpUnariaNode(op, self._fator())
        elif token.tipo == "NÚMERO":
            return NumeroNode(self._consumir("NÚMERO"))
        elif token.tipo == "LPAREN":
            self._consumir("LPAREN")
            resultado = self._expr()
            self._consumir("RPAREN")
            return resultado
        elif token.tipo == "ID":
            return VariavelNode(self._consumir("ID"))
        else:
            raise SyntaxError(f"Fator inválido. Token inesperado: {token}")

    def _termo(self):
        """<termo> ::= <fator> ( (*|/) <fator> )*"""
        node = self._fator()
        while self._token_atual().tipo in ("MULT", "DIV"):
            op = self._consumir(self._token_atual().tipo)
            node = OpBinariaNode(esquerda=node, op=op, direita=self._fator())
        return node

    def _expr(self):
        """<expr> ::= <termo> ( (+|-) <termo> )*"""
        node = self._termo()
        while self._token_atual().tipo in (
            "MAIS",
            "MENOS",
            "MENOR",
            "MENOR_IGUAL",
            "MAIOR",
            "MAIOR_IGUAL",
            "IGUAL",
            "DIFERENTE",
        ):
            op = self._consumir(self._token_atual().tipo)
            node = OpBinariaNode(esquerda=node, op=op, direita=self._termo())
        return node
