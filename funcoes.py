"""Dados, validacoes e funcionalidades do Agente de IA para Camera.

As funcoes deste modulo recebem os dados de que precisam por parametro e,
quando apropriado, retornam resultados. Isso reduz a dependencia de variaveis
globais e facilita a leitura, os testes e a manutencao do programa.
"""

import random
from collections.abc import Sequence
from typing import Optional


# Cada modo e um dicionario. A lista agrupa todos os modos disponiveis e evita
# o uso de varias listas paralelas que precisariam manter a mesma ordem.
MODOS_CAMERA = [
    {
        "nome": "retrato",
        "descricao": "Desfoca o fundo e destaca o rosto do sujeito principal.",
        "onde_usar": (
            "Retratos em estudio, ao ar livre com luz natural ou em ambientes "
            "bem iluminados."
        ),
        "como_usar": (
            "Posicione o rosto no centro do quadro, toque no rosto para focar "
            "e aguarde o desfoque ser aplicado automaticamente."
        ),
        "dicas": [
            "Use luz natural lateral para criar sombras suaves e profundidade no rosto.",
            "Peca para o sujeito olhar levemente acima da camera para um efeito elegante.",
            "Evite zoom digital: aproxime-se para manter a qualidade da imagem.",
        ],
        "sugestao": "Use o modo Retrato com iluminacao frontal para melhores resultados.",
    },
    {
        "nome": "noturno",
        "descricao": "Captura imagens com pouca luz usando exposicao prolongada.",
        "onde_usar": (
            "Ambientes escuros como ruas a noite, shows, festas e cenas com "
            "pouca luz artificial."
        ),
        "como_usar": (
            "Mantenha o dispositivo imovel, toque no ponto mais escuro para "
            "focar e aguarde a captura longa."
        ),
        "dicas": [
            "Apoie o dispositivo em uma superficie solida ou use um tripe.",
            "Evite apontar diretamente para fontes de luz muito fortes.",
            "Experimente focar em um ponto de luz distante para criar profundidade.",
        ],
        "sugestao": "Use o modo Noturno combinado com HDR para ambientes escuros.",
    },
    {
        "nome": "hdr",
        "descricao": "Combina multiplas exposicoes para equilibrar luz e sombra.",
        "onde_usar": (
            "Paisagens com sol forte, ambientes com sombras e luzes ao mesmo "
            "tempo ou cenas de alto contraste."
        ),
        "como_usar": (
            "Enquadre a cena, toque em uma area de meio-tom e deixe a IA "
            "combinar as exposicoes."
        ),
        "dicas": [
            "Use HDR quando o ceu claro contrastar com o solo mais escuro.",
            "Evite HDR em cenas com movimento rapido para nao gerar imagens duplas.",
            "Ative o HDR automatico para o app decidir quando aplica-lo.",
        ],
        "sugestao": "Use o modo HDR em cenas com alto contraste de luz.",
    },
    {
        "nome": "panorama",
        "descricao": "Une varios quadros para formar uma imagem ampla.",
        "onde_usar": (
            "Paisagens abertas, litorais, arquitetura urbana e cenas amplas "
            "que nao cabem em um unico quadro."
        ),
        "como_usar": (
            "Siga a linha guia e mova o dispositivo de maneira lenta e "
            "constante da esquerda para a direita."
        ),
        "dicas": [
            "Defina os pontos de inicio e fim antes de comecar.",
            "Mantenha a linha guia centralizada durante todo o movimento.",
            "Escolha um ambiente com pouco vento para evitar objetos deslocados.",
        ],
        "sugestao": "Use o modo Panorama em ambientes abertos e amplos.",
    },
    {
        "nome": "slow motion",
        "descricao": "Grava em alta velocidade para reproducao lenta.",
        "onde_usar": (
            "Esportes, quedas d'agua, animais em movimento e acoes que "
            "precisem ser observadas em detalhes."
        ),
        "como_usar": (
            "Toque em gravar, aponte para o sujeito e mantenha o enquadramento "
            "firme durante toda a acao."
        ),
        "dicas": [
            "Garanta boa iluminacao para preservar a qualidade da gravacao.",
            "Mantenha o sujeito dentro do quadro durante toda a acao.",
            "Use um fundo simples para destacar o movimento principal.",
        ],
        "sugestao": "Use Slow Motion para registrar movimentos rapidos com detalhes.",
    },
    {
        "nome": "time lapse",
        "descricao": "Comprime longos periodos em poucos segundos de video.",
        "onde_usar": (
            "Por do sol, movimento de nuvens, flores desabrochando, transito "
            "urbano ou construcoes ao longo do tempo."
        ),
        "como_usar": (
            "Fixe o dispositivo, defina o intervalo de captura e deixe o app "
            "registrar as imagens automaticamente."
        ),
        "dicas": [
            "Use um tripe ou uma superficie totalmente fixa.",
            "Evite mudancas bruscas de luz durante a gravacao.",
            "Use intervalos curtos para cenas rapidas e longos para a natureza.",
        ],
        "sugestao": "Use Time Lapse para capturar o por do sol ou as nuvens.",
    },
]


# Constantes escritas em maiusculas indicam dados que nao devem ser alterados.
INSTRUCOES = [
    "Acesse o modo sugerido tocando na aba 'Mais' no menu inferior.",
    "Posicione o dispositivo e toque na tela para definir o ponto de foco.",
    "Ajuste o brilho arrastando o controle lateral exibido apos o foco.",
    "Verifique o enquadramento e estabilize o dispositivo antes de capturar.",
    "Toque no botao de captura para registrar a foto.",
]


# O dicionario associa cada criterio diretamente a sua sugestao de melhoria.
SUGESTOES_CRITERIOS = {
    "Brilho": "Aumente o brilho ou ative o modo HDR na proxima captura.",
    "Contraste": "Ajuste o contraste nas configuracoes avancadas da camera.",
    "Foco": "Toque na tela sobre o sujeito principal para focar corretamente.",
    "Nitidez": "Estabilize o dispositivo ou ative o modo de estabilizacao.",
}


class VoltarAoMenu(Exception):
    """Sinaliza que o usuario digitou '/' para retornar ao menu principal."""


def input_seguro(prompt: str = "") -> str:
    """Le uma entrada, remove espacos e reconhece o atalho de retorno.

    Args:
        prompt: Mensagem apresentada antes da leitura.

    Returns:
        O texto digitado sem espacos nas extremidades.

    Raises:
        VoltarAoMenu: Quando o usuario digita somente '/'.
    """
    entrada = input(prompt).strip()
    if entrada == "/":
        print("\n  [Atalho] Retornando ao menu principal...")
        raise VoltarAoMenu
    return entrada


def validar_sim_nao(pergunta: str) -> str:
    """Solicita e retorna somente uma resposta valida: 's' ou 'n'."""
    while True:
        resposta = input_seguro(f"{pergunta} (s/n): ").lower()
        if resposta in ("s", "n"):
            return resposta
        print("  Invalido. Digite s ou n.")


def validar_opcao(pergunta: str, opcoes_validas: Sequence[str]) -> str:
    """Solicita uma opcao ate que ela esteja entre as opcoes permitidas."""
    while True:
        resposta = input_seguro(pergunta)
        if resposta in opcoes_validas:
            return resposta
        print(f"  Invalido. Opcoes: {', '.join(opcoes_validas)}")


def ler_texto_obrigatorio(pergunta: str) -> str:
    """Solicita e retorna um texto que nao esteja vazio."""
    while True:
        texto = input_seguro(pergunta)
        if texto:
            return texto
        print("  Invalido. Este campo nao pode ficar vazio.")


def escolher_comunicacao() -> str:
    """Pergunta o modo de comunicacao e retorna '1' ou '2'."""
    print("\nComo deseja se comunicar com o agente?")
    print("  1 - Voz (simulada)")
    print("  2 - Texto")
    return validar_opcao("  -> ", ("1", "2"))


def prefixo_comunicacao(comunicacao: str) -> str:
    """Retorna o prefixo visual correspondente ao modo de comunicacao."""
    prefixos = {"1": "[Voz simulada]", "2": "[Texto]"}
    return prefixos.get(comunicacao, "[Agente]")


def exibir_separador(titulo: str) -> None:
    """Exibe um titulo entre separadores visuais padronizados."""
    print("\n" + "=" * 52)
    print(f"  {titulo}")
    print("=" * 52)


def pausar() -> None:
    """Aguarda ENTER antes de devolver o controle ao menu principal."""
    input_seguro("\nPressione ENTER para voltar ao menu...")


def buscar_modo(nome: str) -> Optional[dict]:
    """Busca um modo pelo nome e retorna seu dicionario ou None.

    A expressao geradora evita percorrer o restante da lista depois que o modo
    e encontrado.
    """
    return next((modo for modo in MODOS_CAMERA if modo["nome"] == nome), None)


def adicionar_registro(historico: dict, categoria: str, registro: dict) -> None:
    """Adiciona um registro estruturado a uma categoria do historico."""
    historico[categoria].append(registro)


def guia_passo_a_passo(historico: dict) -> None:
    """Conduz o usuario por uma captura guiada e registra o resultado."""
    try:
        repetir_guia = True

        # O while substitui a chamada recursiva existente no codigo original.
        while repetir_guia:
            exibir_separador("GUIA PASSO A PASSO CONTEXTUAL")

            comunicacao = escolher_comunicacao()
            prefixo = prefixo_comunicacao(comunicacao)

            print(f"\n{prefixo} Qual e o seu objetivo de captura?")
            objetivo = ler_texto_obrigatorio("  -> ")

            print(f"\n  Agente analisando seu objetivo: '{objetivo}'...")
            print("  Selecione o modo mais proximo ao seu objetivo:\n")

            for indice, modo in enumerate(MODOS_CAMERA, start=1):
                print(f"  {indice}. {modo['nome'].capitalize()}")

            # List comprehension cria as opcoes de acordo com a lista de modos.
            opcoes = [str(numero) for numero in range(1, len(MODOS_CAMERA) + 1)]
            escolha = validar_opcao("\n  Modo sugerido (numero): ", opcoes)
            modo = MODOS_CAMERA[int(escolha) - 1]

            print(f"\n  Sugestao do agente: {modo['sugestao']}")
            print(f"\n  Explicacao: {modo['descricao']}")

            if validar_sim_nao("\n  Voce entendeu a explicacao do modo?") == "n":
                print("  [Agente reformula]: Este modo e adequado ao seu objetivo.")
                print(f"  Resumo: {modo['descricao']}")
            else:
                print("  Otimo! Vamos as instrucoes.")

            print(f"\n  Instrucoes para '{modo['nome'].capitalize()}':\n")
            for numero, instrucao in enumerate(INSTRUCOES, start=1):
                compreendeu = "n"
                while compreendeu == "n":
                    print(f"  Passo {numero}: {instrucao}")
                    compreendeu = validar_sim_nao("  Voce entendeu esta instrucao?")
                    if compreendeu == "n":
                        print(f"  [Agente reformula]: Em outras palavras -> {instrucao}")
                print("  Certo! Executando a proxima instrucao...\n")

            print("  Execute a captura agora.")
            atingiu = validar_sim_nao("\n  Voce atingiu seu objetivo de captura?")

            if atingiu == "n":
                print("\n  Nao se preocupe! O agente sugere revisar os passos.")
                repetir = validar_sim_nao("  Deseja realizar uma nova tentativa guiada?")
                resultado = "nova tentativa solicitada" if repetir == "s" else "nao atingido"
                adicionar_registro(
                    historico,
                    "guias",
                    {"objetivo": objetivo, "modo": modo["nome"], "resultado": resultado},
                )
                repetir_guia = repetir == "s"
            else:
                print("\n  Captura realizada com sucesso!")
                adicionar_registro(
                    historico,
                    "guias",
                    {"objetivo": objetivo, "modo": modo["nome"], "resultado": "atingido"},
                )

                print("  O agente esta analisando sua foto capturada...")
                if validar_sim_nao("  Deseja uma sugestao para a proxima captura?") == "s":
                    print("  -> Fixe o foco no sujeito principal.")
                    print("  -> Ajuste o brilho antes de capturar.")
                    print("  -> Use estabilizacao se a foto ficar tremida.")
                else:
                    print("  Tudo certo! Foto aprovada pelo agente.")
                repetir_guia = False

        pausar()
    except VoltarAoMenu:
        # Encerrar esta funcao devolve naturalmente o controle ao menu do main.
        return


def acionar_modo(historico: dict) -> None:
    """Orienta o acionamento de um modo e registra a escolha do usuario."""
    try:
        outro = "s"
        while outro == "s":
            exibir_separador("ACIONAMENTO DE MODOS POR PEDIDO DO USUARIO")
            comunicacao = escolher_comunicacao()
            prefixo = prefixo_comunicacao(comunicacao)

            print(f"\n{prefixo} Qual modo deseja acionar?")
            for indice, modo_disponivel in enumerate(MODOS_CAMERA, start=1):
                print(f"  {indice}. {modo_disponivel['nome'].capitalize()}")

            pedido = ler_texto_obrigatorio("\n  Digite o nome do modo: ").lower()
            modo = buscar_modo(pedido)

            if modo is None:
                print(f"\n  ATENCAO: A funcao '{pedido}' esta indisponivel.")
                adicionar_registro(
                    historico,
                    "modos",
                    {"modo": pedido, "status": "indisponivel"},
                )
            else:
                print(f"\n  Modo '{modo['nome'].capitalize()}' encontrado!")
                print(f"\n  ONDE USAR:\n  -> {modo['onde_usar']}")
                print(f"\n  COMO USAR:\n  -> {modo['como_usar']}")
                print("\n  3 DICAS PARA APLICAR COM PROFISSIONALISMO:")
                for numero, dica in enumerate(modo["dicas"], start=1):
                    print(f"  {numero}. {dica}")

                if validar_sim_nao("\n  Deseja uma explicacao mais detalhada?") == "s":
                    print(f"\n  {modo['descricao']}")
                    print(f"  Dica principal: {modo['dicas'][0]}")

                confirma = validar_sim_nao(
                    f"\n  Confirma o acionamento de '{modo['nome'].capitalize()}'?"
                )
                status = "ativado" if confirma == "s" else "cancelado pelo usuario"
                adicionar_registro(
                    historico,
                    "modos",
                    {"modo": modo["nome"], "status": status},
                )

                if confirma == "s":
                    print(f"\n  Modo '{modo['nome'].capitalize()}' acionado!")
                    print(f"  Lembre-se: {modo['dicas'][0]}")
                else:
                    print("\n  A acao foi cancelada.")

            outro = validar_sim_nao("\n  Deseja acionar outro modo?")

        pausar()
    except VoltarAoMenu:
        return


def sugestao_melhorias(historico: dict) -> None:
    """Simula a analise de uma foto e apresenta melhorias ao usuario."""
    try:
        exibir_separador("SUGESTAO DE MELHORIAS POS-FOTO")
        comunicacao = escolher_comunicacao()
        prefixo = prefixo_comunicacao(comunicacao)

        print(f"\n{prefixo} Informe o nome da foto salva para analise.")
        foto = ler_texto_obrigatorio("  -> ")

        print(f"\n  IA analisando '{foto}'...")
        print("  Escala: 1 = ruim | 5 = otimo\n")

        # Dict comprehension gera uma nota simulada para cada criterio.
        notas = {
            criterio: random.randint(1, 5)
            for criterio in SUGESTOES_CRITERIOS
        }

        for criterio, nota in notas.items():
            print(f"  {criterio}: {nota}/5")

        # Outra compreensao seleciona somente os pontos que precisam melhorar.
        pontos_melhoria = {
            criterio: nota
            for criterio, nota in notas.items()
            if nota < 4
        }

        if not pontos_melhoria:
            print(f"\n  Foto aprovada! Nenhuma melhoria foi identificada em '{foto}'.")
            status = "aprovada"
        else:
            print(f"\n  Foram identificados {len(pontos_melhoria)} ponto(s) para melhorar.")
            deseja_ver = validar_sim_nao("  Voce deseja ver o feedback da IA?")

            if deseja_ver == "n":
                print(f"\n  A foto original '{foto}' foi mantida.")
                status = "feedback recusado"
            else:
                print("\n  Apontamentos do feedback:")
                for criterio, nota in pontos_melhoria.items():
                    print(f"  {criterio} ({nota}/5): {SUGESTOES_CRITERIOS[criterio]}")

                aceita = validar_sim_nao("\n  Voce aceita a aplicacao do feedback?")
                if aceita == "s":
                    print(f"\n  Melhorias aplicadas em '{foto}_melhorada'.")
                    status = "melhorias aplicadas"
                else:
                    print(f"\n  A foto original '{foto}' foi mantida.")
                    status = "melhorias recusadas"

        adicionar_registro(
            historico,
            "fotos",
            {"foto": foto, "notas": notas, "status": status},
        )
        pausar()
    except VoltarAoMenu:
        return


def formatar_registro(registro: dict) -> str:
    """Transforma um registro em texto legivel para exibicao."""
    partes = [f"{chave}: {valor}" for chave, valor in registro.items()]
    return " | ".join(partes)


def exibir_historico(historico: dict) -> None:
    """Exibe todos os registros produzidos durante a sessao atual."""
    try:
        exibir_separador("HISTORICO DA SESSAO")

        titulos = {
            "guias": "Guias realizados",
            "modos": "Modos consultados",
            "fotos": "Fotos analisadas",
        }

        for categoria, titulo in titulos.items():
            registros = historico[categoria]
            print(f"\n  {titulo}: {len(registros)}")

            if not registros:
                print("  (nenhum registro)")
            else:
                for registro in registros:
                    print(f"  - {formatar_registro(registro)}")

        pausar()
    except VoltarAoMenu:
        return
