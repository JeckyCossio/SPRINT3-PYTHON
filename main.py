"""Ponto de entrada. Execute: python main.py (Python 3.9 ou superior)."""
from persistencia import ARQUIVO_HISTORICO, carregar_historico, criar_sessao, registrar
from funcoes import (exibir_menu, preparar_camera, consultar_condicoes,
                     exibir_historico, excluir_historico, finalizar)


def menu_principal(caminho=ARQUIVO_HISTORICO):
    dados, erro = carregar_historico(caminho)
    if erro:
        print(erro)
        print(f'Arquivo preservado: {caminho}')
        print('Faça uma cópia de segurança e corrija ou renomeie esse arquivo antes de reiniciar.')
        return
    while True:
        sessao = None
        try:
            exibir_menu()
            opcao = input('Opção: ').strip()
            if opcao == '0':
                print('Encerrando o JOVI AI. Até logo!')
                return
            if opcao == '/':
                continue
            if opcao in ('1', '2'):
                tipo = 'preparação simulada' if opcao == '1' else 'consulta meteorológica'
                sessao = criar_sessao(dados, tipo)
                registrar(sessao, 'sistema', 'Menu principal: 1 - Preparação; 2 - Clima.')
                registrar(sessao, 'usuario', opcao)
                if opcao == '1':
                    preparar_camera(dados, sessao, caminho)
                else:
                    consultar_condicoes(dados, sessao, caminho)
            elif opcao == '3':
                exibir_historico(dados)
            elif opcao == '4':
                dados = excluir_historico(dados, caminho)
            else:
                print('Opção inválida. Escolha uma das opções do menu.')
        except (EOFError, KeyboardInterrupt):
            if sessao is not None:
                finalizar(dados, sessao, 'interrompida', caminho)
            print('\nEntrada encerrada. Finalizando o programa com segurança.')
            return


if __name__ == '__main__':
    menu_principal()
