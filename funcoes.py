"""Interação por terminal, reaproveitando validação e retorno ao menu da Sprint 3."""
from datetime import datetime
from persistencia import agora, registrar, salvar_historico, excluir_sessoes
from regras import CATEGORIAS, PERFIS, decidir_configuracao
from clima import buscar_cidades, nome_cidade, consultar_clima, formatar_clima


def gravar(dados, caminho):
    erro = salvar_historico(dados, caminho)
    if erro:
        print(f'ATENÇÃO: {erro}')
    return erro is None


def dizer(dados, sessao, texto, caminho):
    print('\n' + texto)
    registrar(sessao, 'sistema', texto)
    gravar(dados, caminho)


def perguntar(dados, sessao, texto, caminho):
    """None sinaliza cancelamento; não usamos exceção personalizada/classe."""
    dizer(dados, sessao, texto + '\n(/ para cancelar e voltar ao menu)', caminho)
    resposta = input('> ').strip()
    registrar(sessao, 'usuario', resposta)
    gravar(dados, caminho)
    if resposta == '/':
        return None
    return resposta


def escolher(dados, sessao, pergunta, opcoes, caminho):
    menu = pergunta + '\n' + '\n'.join(f'{k} - {v}' for k, v in opcoes.items())
    while True:
        resposta = perguntar(dados, sessao, menu, caminho)
        if resposta is None or resposta in opcoes:
            return resposta
        dizer(dados, sessao, 'Opção inválida. Escolha um dos números apresentados.', caminho)


def finalizar(dados, sessao, status, caminho):
    sessao['status'] = status
    sessao['fim'] = agora()
    dizer(dados, sessao, f'Sessão {status}. Retornando ao menu principal.', caminho)


def fluxo_clima(dados, sessao, caminho):
    """Pode integrar uma preparação ou funcionar como consulta independente."""
    while True:
        nome = perguntar(dados, sessao, 'Qual cidade deseja consultar? Digite o nome da cidade.', caminho)
        if nome is None:
            return None, 'cancelada'
        if 2 <= len(nome) <= 100 and any(letra.isalpha() for letra in nome):
            break
        dizer(dados, sessao, 'Informe um nome de cidade com 2 a 100 caracteres.', caminho)
    dizer(dados, sessao, 'Consultando localização na API Open-Meteo...', caminho)
    cidades, erro = buscar_cidades(nome)
    if erro:
        dizer(dados, sessao, erro, caminho)
        return None, 'falha na API'
    if not cidades:
        dizer(dados, sessao, 'Cidade não encontrada. Confira o nome e inicie outra consulta.', caminho)
        return None, 'cidade não encontrada'
    opcoes = {str(i): nome_cidade(c) for i, c in enumerate(cidades, 1)}
    escolha = escolher(dados, sessao, 'Selecione a cidade (confira estado e país):', opcoes, caminho)
    if escolha is None:
        return None, 'cancelada'
    cidade = cidades[int(escolha) - 1]
    dizer(dados, sessao, 'Consultando condições atuais e horários solares de hoje...', caminho)
    clima, erro = consultar_clima(cidade)
    if erro:
        dizer(dados, sessao, erro, caminho)
        return None, 'falha na API'
    dizer(dados, sessao, formatar_clima(clima), caminho)
    return clima, 'concluída'


def preparar_camera(dados, sessao, caminho):
    dizer(dados, sessao, 'PREPARAÇÃO AUTOMÁTICA SIMULADA\n'
          'Não acessamos câmera, imagens, microfone ou IA. O disparo final é seu.', caminho)
    autoriza = escolher(dados, sessao, 'Autoriza iniciar esta simulação automática?',
                        {'1': 'Sim', '2': 'Não'}, caminho)
    if autoriza != '1':
        finalizar(dados, sessao, 'cancelada', caminho)
        return
    perguntas = [
        ('categoria', 'O que você quer fotografar?', CATEGORIAS),
        ('ambiente', 'Onde está a cena?', {'1': 'Ambiente interno', '2': 'Ambiente externo'}),
        ('luz', 'Como está a iluminação real da cena?',
         {'1': 'Baixa (pouca luz)', '2': 'Suficiente e uniforme',
          '3': 'Alto contraste (áreas muito claras e escuras)'}),
        ('movimento', 'O assunto principal está em movimento?', {'1': 'Sim', '2': 'Não'}),
        ('perfil', 'Qual perfil de recursos deseja simular?',
         {k: v['nome'] for k, v in PERFIS.items()}),
    ]
    respostas = {}
    for campo, pergunta, opcoes in perguntas:
        valor = escolher(dados, sessao, pergunta, opcoes, caminho)
        if valor is None:
            finalizar(dados, sessao, 'cancelada', caminho)
            return
        respostas[campo] = valor
    cenario = {'categoria': respostas['categoria'],
               'ambiente': 'externo' if respostas['ambiente'] == '2' else 'interno',
               'luz': {'1': 'baixa', '2': 'uniforme', '3': 'contraste'}[respostas['luz']],
               'movimento': 'sim' if respostas['movimento'] == '1' else 'não'}
    clima = None
    if cenario['ambiente'] == 'externo':
        consultar = escolher(dados, sessao, 'Deseja consultar o clima antes de continuar?',
                             {'1': 'Sim', '2': 'Não'}, caminho)
        if consultar is None:
            finalizar(dados, sessao, 'cancelada', caminho)
            return
        if consultar == '1':
            clima, status = fluxo_clima(dados, sessao, caminho)
            if status == 'cancelada':
                finalizar(dados, sessao, 'cancelada', caminho)
                return
            if clima is None:
                dizer(dados, sessao, 'Continuando sem dados meteorológicos; '
                      'serão usadas somente as condições informadas por você.', caminho)
    resultado = decidir_configuracao(cenario, PERFIS[respostas['perfil']])
    sessao['resultado'] = {'cenario': cenario, 'configuracao': resultado, 'clima': clima}
    texto = (f"RESULTADO SIMULADO — {CATEGORIAS[cenario['categoria']]}\n"
             f"Perfil: {resultado['perfil']}\nModo: {resultado['modo']}\n"
             f"HDR: {'ativado' if resultado['hdr'] else 'desativado'}\n"
             f"Foco: {resultado['foco']}\nExposição: {resultado['exposicao']}\n"
             'Flash: desativado\n')
    texto += '\n'.join(resultado['motivos'] + ['Limitação: ' + a for a in resultado['avisos']])
    texto += ('\nPreparação concluída apenas na simulação. Nenhuma configuração real foi alterada.'
              '\nNa experiência proposta, você decide quando pressionar o botão de captura.')
    dizer(dados, sessao, texto, caminho)
    finalizar(dados, sessao, 'concluída', caminho)


def consultar_condicoes(dados, sessao, caminho):
    resultado, status = fluxo_clima(dados, sessao, caminho)
    sessao['resultado'] = resultado
    finalizar(dados, sessao, status, caminho)


def listar_sessoes(dados):
    for numero, sessao in enumerate(dados['sessoes'], 1):
        print(f"{numero} - {sessao['inicio']} | {sessao['tipo']} | {sessao['status']}")


def exibir_historico(dados):
    """Consulta administrativa não gera nova conversa no histórico."""
    if not dados['sessoes']:
        print('\nNenhuma sessão registrada.')
        return
    listar_sessoes(dados)
    while True:
        escolha = input('Número da sessão para ler (/ para voltar): ').strip()
        if escolha == '/':
            return
        if len(escolha) <= 9 and escolha.isdecimal() and 1 <= int(escolha) <= len(dados['sessoes']):
            sessao = dados['sessoes'][int(escolha) - 1]
            print(f"\nSessão {sessao['id']} — {sessao['status']}")
            for mensagem in sessao['mensagens']:
                print(f"[{mensagem['horario']}] {mensagem['papel']}: {mensagem['texto']}")
            return
        print('Número inválido. Escolha uma sessão da lista.')


def excluir_historico(dados, caminho):
    if not dados['sessoes']:
        print('\nNenhuma sessão para excluir.')
        return dados
    listar_sessoes(dados)
    while True:
        escolha = input('Número da sessão, T para todas ou / para voltar: ').strip().lower()
        if escolha == '/':
            return dados
        if escolha == 't':
            identificador = None
            alvo = 'TODAS as sessões'
            break
        if len(escolha) <= 9 and escolha.isdecimal() and 1 <= int(escolha) <= len(dados['sessoes']):
            identificador = dados['sessoes'][int(escolha) - 1]['id']
            alvo = f'a sessão {escolha}'
            break
        print('Opção inválida.')
    while True:
        confirma = input(f'Excluir {alvo}? Digite s ou n (/ cancela): ').strip().lower()
        if confirma in ('n', '/'):
            print('Exclusão cancelada.')
            return dados
        if confirma == 's':
            novos = excluir_sessoes(dados, identificador)
            if gravar(novos, caminho):
                print('Exclusão concluída.')
                return novos
            print('Exclusão não concluída. Os dados anteriores foram mantidos.')
            return dados
        print('Digite s ou n.')


def exibir_menu():
    print('\n' + '=' * 62)
    print('JOVI AI — SPRINT 4 | Open Source Consulting')
    print('Horário do sistema: ' + datetime.now().astimezone().strftime('%d/%m/%Y %H:%M:%S %z'))
    print('1 - Iniciar preparação automática simulada')
    print('2 - Consultar condições para fotografar ao ar livre')
    print('3 - Visualizar sessões anteriores')
    print('4 - Excluir histórico')
    print('0 - Sair')
    print('/ - Cancelar uma operação e voltar ao menu')
    print('=' * 62)
