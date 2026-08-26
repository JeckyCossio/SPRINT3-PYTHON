"""Ponto de entrada do Agente de IA para Camera.

Este arquivo possui somente as responsabilidades principais do programa:
criar os dados da sessao, apresentar o menu e chamar as funcionalidades
implementadas no modulo ``funcoes``.
"""

from funcoes import (
    VoltarAoMenu,
    acionar_modo,
    exibir_historico,
    guia_passo_a_passo,
    input_seguro,
    sugestao_melhorias,
)


def criar_historico() -> dict:
    """Cria e retorna o dicionario que armazena o historico da sessao.

    Cada chave representa uma funcionalidade e possui uma lista de registros.
    O historico existe somente enquanto o programa estiver em execucao.
    """
    return {
        "guias": [],
        "modos": [],
        "fotos": [],
    }


def exibir_menu() -> None:
    """Apresenta as opcoes disponiveis no menu principal."""
    print("\n====================================================")
    print("        AGENTE DE IA PARA CAMERA - SPRINT 2")
    print("====================================================")
    print("  1 - Guia Passo a Passo Contextual")
    print("  2 - Acionamento de Modos")
    print("  3 - Sugestao de Melhorias Pos-Foto")
    print("  4 - Historico da sessao")
    print("  0 - Sair")
    print("  / - Voltar ao menu (disponivel em qualquer entrada)")
    print("====================================================")


def menu_principal() -> None:
    """Controla o menu principal ate que o usuario escolha sair.

    O mesmo dicionario de historico e passado por parametro para todas as
    funcionalidades. Dessa forma, nao precisamos usar variaveis globais para
    guardar os dados produzidos durante a sessao.
    """
    historico = criar_historico()

    while True:
        exibir_menu()

        try:
            opcao = input_seguro("  Opcao: ")
        except VoltarAoMenu:
            # Se '/' for digitado no proprio menu, apenas o mostramos de novo.
            continue

        # if/elif mantem o programa compativel tambem com o Python 3.9.
        if opcao == "1":
            guia_passo_a_passo(historico)
        elif opcao == "2":
            acionar_modo(historico)
        elif opcao == "3":
            sugestao_melhorias(historico)
        elif opcao == "4":
            exibir_historico(historico)
        elif opcao == "0":
            print("\n  Encerrando o agente. Ate logo!")
            break
        else:
            print("\n  Opcao invalida. Escolha uma das opcoes do menu.")


if __name__ == "__main__":
    # Este bloco impede que o menu seja iniciado caso main.py seja importado.
    menu_principal()
