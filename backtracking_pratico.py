"""
=============================================================
  LABORATÓRIO DE PROGRAMAÇÃO AVANÇADA — BACKTRACKING
  Parte Prática: Dois Problemas Resolvidos com Backtracking
  
  Problemas:
    1. N-Rainhas
    2. Sudoku Solver

  Autores: Dário Puíssa João | Félix Bongue
  Curso: Ciência da Computação — 3.º Ano
  Disciplina: Laboratório de Programação Avançada
=============================================================
"""


# ==============================================================
# PROBLEMA 1: N-RAINHAS
# ==============================================================
# Descrição:
#   Posicionar N rainhas em um tabuleiro N×N de forma que nenhuma
#   rainha ataque outra (nem na mesma linha, coluna ou diagonal).
#
# Abordagem Backtracking:
#   - Colocamos uma rainha por linha (decisão sequencial).
#   - Para cada coluna tentada, verificamos conflitos (rejeição).
#   - Se houver conflito, tentamos a próxima coluna (backtrack).
#   - Se não houver coluna válida, retrocedemos à linha anterior.
# ==============================================================

def resolver_n_rainhas(n):
    """
    Resolve o problema das N-Rainhas usando backtracking.
    
    Retorna uma lista com todas as soluções encontradas.
    Cada solução é uma lista de N inteiros onde solucao[i]
    indica a coluna onde a rainha da linha i foi posicionada.
    """
    solucoes = []
    tabuleiro = []  # tabuleiro[i] = coluna da rainha na linha i

    def e_valida(linha, coluna):
        """
        Função de REJEIÇÃO:
        Verifica se colocar uma rainha em (linha, coluna) conflita
        com alguma rainha já posicionada.
        """
        for l in range(linha):
            c = tabuleiro[l]
            # Mesma coluna
            if c == coluna:
                return False
            # Mesma diagonal (diferença de linhas == diferença de colunas)
            if abs(c - coluna) == abs(l - linha):
                return False
        return True  # Posição válida → continuar

    def backtrack(linha):
        """
        Função principal de backtracking.
        Tenta posicionar uma rainha em cada coluna da linha atual.
        """
        # Função de ACEITAÇÃO: todas as N linhas foram preenchidas
        if linha == n:
            solucoes.append(list(tabuleiro))
            return

        # Geração de extensões: testar cada coluna da linha atual
        for coluna in range(n):
            if e_valida(linha, coluna):
                tabuleiro.append(coluna)       # Fazer escolha
                backtrack(linha + 1)           # Avançar recursivamente
                tabuleiro.pop()                # DESFAZER escolha (backtrack)

    backtrack(0)
    return solucoes


def imprimir_tabuleiro(solucao, n):
    """Exibe o tabuleiro de uma solução de forma visual."""
    separador = "+" + ("---+" * n)
    print(separador)
    for linha in range(n):
        fila = "|"
        for coluna in range(n):
            if solucao[linha] == coluna:
                fila += " Q |"
            else:
                fila += "   |"
        print(fila)
        print(separador)


def demo_n_rainhas():
    print("=" * 60)
    print("  PROBLEMA 1: N-RAINHAS")
    print("=" * 60)

    for n in [4, 5, 6]:
        solucoes = resolver_n_rainhas(n)
        print(f"\n[N = {n}] → {len(solucoes)} solução(ões) encontrada(s)")

    # Exibir a primeira solução para N=6 visualmente
    n = 6
    solucoes = resolver_n_rainhas(n)
    print(f"\nPrimeira solução para N={n}:")
    print(f"  Representação: {solucoes[0]}")
    print(f"  (solucao[linha] = coluna onde a rainha foi posicionada)\n")
    imprimir_tabuleiro(solucoes[0], n)

    # Estatística de contagem para N maiores
    print("\nContagem de soluções por N:")
    print(f"  {'N':>4} | {'Soluções':>10} | {'Nós visitados (aprox.)':>22}")
    print(f"  {'-'*4}-+-{'-'*10}-+-{'-'*22}")
    for n in range(1, 10):
        s = resolver_n_rainhas(n)
        print(f"  {n:>4} | {len(s):>10}")


# ==============================================================
# PROBLEMA 2: SUDOKU SOLVER
# ==============================================================
# Descrição:
#   Preencher um tabuleiro 9×9 com os dígitos 1–9, respeitando:
#     - Cada linha contém cada dígito exatamente uma vez.
#     - Cada coluna contém cada dígito exatamente uma vez.
#     - Cada bloco 3×3 contém cada dígito exatamente uma vez.
#   Células com valor 0 representam células em branco.
#
# Abordagem Backtracking:
#   - Encontramos a próxima célula vazia.
#   - Tentamos dígitos de 1 a 9.
#   - Função de rejeição verifica linha, coluna e bloco.
#   - Se nenhum dígito for válido, retrocedemos (backtrack).
# ==============================================================

def resolver_sudoku(tabuleiro):
    """
    Resolve o Sudoku usando backtracking.
    Modifica o tabuleiro in-place.
    
    Retorna True se o Sudoku foi resolvido, False caso contrário.
    O tabuleiro é uma lista de 9 listas de 9 inteiros.
    Células vazias são representadas por 0.
    """

    def encontrar_celula_vazia():
        """Encontra a próxima célula com valor 0 (vazia)."""
        for linha in range(9):
            for coluna in range(9):
                if tabuleiro[linha][coluna] == 0:
                    return linha, coluna
        return None  # Nenhuma célula vazia → tabuleiro completo

    def e_valido(linha, coluna, num):
        """
        Função de REJEIÇÃO:
        Verifica se 'num' pode ser colocado em (linha, coluna)
        sem violar as regras do Sudoku.
        """
        # Verificar linha
        if num in tabuleiro[linha]:
            return False

        # Verificar coluna
        if num in [tabuleiro[l][coluna] for l in range(9)]:
            return False

        # Verificar bloco 3×3
        inicio_linha = (linha // 3) * 3
        inicio_coluna = (coluna // 3) * 3
        for l in range(inicio_linha, inicio_linha + 3):
            for c in range(inicio_coluna, inicio_coluna + 3):
                if tabuleiro[l][c] == num:
                    return False

        return True  # Número válido → continuar

    def backtrack():
        """
        Função principal de backtracking.
        """
        celula = encontrar_celula_vazia()

        # Função de ACEITAÇÃO: não há células vazias → Sudoku resolvido
        if celula is None:
            return True

        linha, coluna = celula

        # Geração de extensões: testar dígitos 1 a 9
        for num in range(1, 10):
            if e_valido(linha, coluna, num):
                tabuleiro[linha][coluna] = num      # Fazer escolha
                
                if backtrack():                     # Avançar recursivamente
                    return True
                
                tabuleiro[linha][coluna] = 0        # DESFAZER escolha (backtrack)

        return False  # Nenhum número funcionou → retroceder

    return backtrack()


def imprimir_sudoku(tabuleiro, titulo="Tabuleiro"):
    """Exibe o tabuleiro de Sudoku de forma formatada."""
    print(f"\n{titulo}:")
    separador_grosso  = "╔═══╤═══╤═══╦═══╤═══╤═══╦═══╤═══╤═══╗"
    separador_medio   = "╠═══╪═══╪═══╬═══╪═══╪═══╬═══╪═══╪═══╣"
    separador_fino    = "╟───┼───┼───╫───┼───┼───╫───┼───┼───╢"
    separador_base    = "╚═══╧═══╧═══╩═══╧═══╧═══╩═══╧═══╧═══╝"

    print(separador_grosso)
    for i, linha in enumerate(tabuleiro):
        if i > 0 and i % 3 == 0:
            print(separador_medio)
        elif i > 0:
            print(separador_fino)
        linha_str = "║"
        for j, val in enumerate(linha):
            celula = f" {val} " if val != 0 else " · "
            sep = "║" if (j + 1) % 3 == 0 else "│"
            linha_str += celula + sep
        print(linha_str)
    print(separador_base)


def demo_sudoku():
    print("\n" + "=" * 60)
    print("  PROBLEMA 2: SUDOKU SOLVER")
    print("=" * 60)

    # Puzzle de exemplo (dificuldade média)
    # 0 representa células em branco
    puzzle = [
        [5, 3, 0,  0, 7, 0,  0, 0, 0],
        [6, 0, 0,  1, 9, 5,  0, 0, 0],
        [0, 9, 8,  0, 0, 0,  0, 6, 0],

        [8, 0, 0,  0, 6, 0,  0, 0, 3],
        [4, 0, 0,  8, 0, 3,  0, 0, 1],
        [7, 0, 0,  0, 2, 0,  0, 0, 6],

        [0, 6, 0,  0, 0, 0,  2, 8, 0],
        [0, 0, 0,  4, 1, 9,  0, 0, 5],
        [0, 0, 0,  0, 8, 0,  0, 7, 9],
    ]

    # Fazer cópia para não modificar o original ao exibir
    import copy
    puzzle_original = copy.deepcopy(puzzle)

    imprimir_sudoku(puzzle_original, "Puzzle (antes de resolver)")

    resolvido = resolver_sudoku(puzzle)

    if resolvido:
        imprimir_sudoku(puzzle, "Solução (após backtracking)")
    else:
        print("\n[ERRO] Este Sudoku não tem solução.")


# ==============================================================
# PONTO DE ENTRADA
# ==============================================================

if __name__ == "__main__":
    demo_n_rainhas()
    demo_sudoku()

    print("\n" + "=" * 60)
    print("  FIM DA EXECUÇÃO")
    print("=" * 60)
