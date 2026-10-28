"""Verificações automatizadas sem classes. Execute: python tests/verificar.py."""
import io
import json
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import requests
import clima
from main import menu_principal
from persistencia import carregar_historico, salvar_historico, novo_historico
from regras import decidir_configuracao, PERFIS

TOTAL = 0


def verificar(condicao, descricao):
    global TOTAL
    assert condicao, descricao
    TOTAL += 1
    print('OK:', descricao)


def executar(entradas, arquivo):
    saida = io.StringIO()
    with patch('builtins.input', side_effect=entradas), redirect_stdout(saida):
        menu_principal(arquivo)
    return saida.getvalue()


def testar_regras():
    def regra(categoria, luz='uniforme', movimento='não', perfil='1'):
        return decidir_configuracao({'categoria': categoria, 'luz': luz,
                                     'movimento': movimento, 'ambiente': 'interno'}, PERFIS[perfil])
    verificar(regra('1')['modo'] == 'Retrato', 'retrato com luz uniforme')
    verificar(regra('2', 'baixa')['modo'] == 'Noturno', 'grupo parado com pouca luz')
    verificar(regra('2', 'baixa', 'sim')['modo'] == 'Foto', 'movimento evita exposição noturna longa')
    verificar(regra('3')['modo'] == 'Documento', 'documento prioriza legibilidade')
    verificar(regra('4', 'baixa')['modo'] == 'Foto' and not regra('4', 'contraste')['hdr'],
              'slide preserva projeção sem HDR ou modo noturno')
    verificar(regra('5', 'contraste')['hdr'], 'HDR em paisagem parada com contraste')
    verificar(not regra('5', 'contraste', 'sim')['hdr'], 'movimento impede HDR')
    verificar(regra('1', perfil='2')['modo'] == 'Foto', 'fallback de retrato indisponível')
    verificar(not regra('5', 'contraste', perfil='2')['hdr'], 'fallback de HDR indisponível')
    for categoria in ('1', '2', '3', '4', '5'):
        for luz in ('uniforme', 'baixa', 'contraste'):
            for movimento in ('sim', 'não'):
                for perfil in ('1', '2'):
                    r = regra(categoria, luz, movimento, perfil)
                    assert r['modo'] in PERFIS[perfil]['modos']
                    assert not (r['hdr'] and r['modo'] == 'Noturno')
    verificar(True, '60 combinações respeitam compatibilidade e separação de HDR/Noturno')


def testar_persistencia_terminal():
    with tempfile.TemporaryDirectory() as pasta:
        arquivo = Path(pasta) / 'dados' / 'historico.json'
        verificar(carregar_historico(arquivo)[0] == novo_historico(), 'primeira execução sem arquivo')
        # Menu inválido; consentimento; categoria; ambiente; luz; movimento; perfil; sair.
        saida = executar(['9', '1', '1', '1', '1', '2', '2', '1', '0'], arquivo)
        dados, erro = carregar_historico(arquivo)
        sessao = dados['sessoes'][0]
        verificar(erro is None and sessao['status'] == 'concluída', 'fluxo completo persistido')
        verificar('Opção inválida' in saida and 'Encerrando' in saida, 'menu inválido, retorno e saída')
        verificar(sessao['resultado']['configuracao']['modo'] == 'Retrato', 'resultado salvo')
        verificar(any(m['papel'] == 'usuario' for m in sessao['mensagens']) and
                  any('Autoriza' in m['texto'] for m in sessao['mensagens']), 'perguntas e respostas completas')
        saida = executar(['3', '1', '0'], arquivo)
        verificar('Autoriza' in saida and len(carregar_historico(arquivo)[0]['sessoes']) == 1,
                  'histórico recuperado após reinício; leitura não duplica sessões')
        executar(['1', '/','0'], arquivo)
        verificar(carregar_historico(arquivo)[0]['sessoes'][-1]['status'] == 'cancelada', 'atalho / registrado')
        executar(['1', '2', '0'], arquivo)
        verificar(carregar_historico(arquivo)[0]['sessoes'][-1]['status'] == 'cancelada', 'recusa do consentimento')
        executar(['1', KeyboardInterrupt()], arquivo)
        verificar(carregar_historico(arquivo)[0]['sessoes'][-1]['status'] == 'interrompida', 'Ctrl+C preserva sessão')
        with patch('funcoes.buscar_cidades', return_value=(None, 'Erro na API: provável falta de internet.')):
            saida = executar(['1', '1', '5', '2', '1', '2', '1', '1', 'São Paulo', '0'], arquivo)
        verificar('Continuando sem dados meteorológicos' in saida and
                  carregar_historico(arquivo)[0]['sessoes'][-1]['status'] == 'concluída',
                  'API offline não bloqueia preparação simulada')
        quantidade = len(carregar_historico(arquivo)[0]['sessoes'])
        executar(['4', 't', 'n', '0'], arquivo)
        verificar(len(carregar_historico(arquivo)[0]['sessoes']) == quantidade, 'exclusão recusada preserva dados')
        executar(['4', '1', 's', '0'], arquivo)
        verificar(len(carregar_historico(arquivo)[0]['sessoes']) == quantidade - 1, 'exclusão individual persistida')
        executar(['4', 't', 's', '0'], arquivo)
        verificar(not carregar_historico(arquivo)[0]['sessoes'], 'exclusão total sem recriar sessões')
        arquivo.write_text('{quebrado', encoding='utf-8')
        saida = executar([], arquivo)
        verificar('Arquivo preservado' in saida and arquivo.read_text() == '{quebrado', 'JSON corrompido nunca sobrescrito')
        arquivo.write_text('{"versao": 1, "sessoes": [null]}', encoding='utf-8')
        verificar(carregar_historico(arquivo)[0] is None, 'estrutura JSON inválida rejeitada')
        bloqueio = Path(pasta) / 'bloqueio'
        bloqueio.write_text('arquivo ocupa caminho da pasta')
        verificar(salvar_historico(novo_historico(), bloqueio / 'dados.json') is not None,
                  'falha de gravação devolve erro explícito')


def testar_api():
    for excecao, trecho in [
        (requests.exceptions.ConnectionError(), 'provável falta de internet'),
        (requests.exceptions.Timeout(), 'demorou'),
        (requests.exceptions.HTTPError(), 'HTTP'),
        (ValueError(), 'JSON válido'),
    ]:
        with patch('clima.requests.get', side_effect=excecao):
            dados, erro = clima.obter_json('https://exemplo.test', {})
        verificar(dados is None and trecho in erro, f'tratamento API: {trecho}')
    with patch('clima.obter_json', return_value=({'results': []}, None)):
        verificar(clima.buscar_cidades('Xxxxx')[0] == [], 'cidade não encontrada')
    with patch('clima.obter_json', return_value=({'results': [{'name': 'X', 'latitude': None}]}, None)):
        verificar(clima.buscar_cidades('Xxxxx')[0] is None, 'coordenadas incompletas rejeitadas')
    cidade = {'name': 'Teste', 'latitude': -23, 'longitude': -46}
    with patch('clima.obter_json', return_value=({'current': {}}, None)):
        verificar(clima.consultar_clima(cidade)[0] is None, 'resposta meteorológica incompleta rejeitada')
    resposta = {'current': {'time': 1793217600, 'temperature_2m': 20,
                           'precipitation': 0, 'cloud_cover': 10, 'is_day': 1},
                'daily': {'sunrise': [1793175600], 'sunset': [1793220000]},
                'utc_offset_seconds': -10800, 'timezone': 'America/Sao_Paulo'}
    with patch('clima.obter_json', return_value=(resposta, None)):
        resultado, erro = clima.consultar_clima(cidade)
    verificar(erro is None and 'Horário do sistema' in clima.formatar_clima(resultado), 'clima válido e relógios separados')
    with tempfile.TemporaryDirectory() as pasta:
        arquivo = Path(pasta) / 'historico.json'
        with patch('funcoes.buscar_cidades', return_value=([cidade, dict(cidade, name='Outra')], None)), \
             patch('funcoes.consultar_clima', return_value=(resultado, None)):
            saida = executar(['2', '', 'Teste', '9', '1', '0'], arquivo)
        dados = carregar_historico(arquivo)[0]
        verificar(dados['sessoes'][0]['status'] == 'concluída' and 'Selecione a cidade' in saida,
                  'consulta meteorológica com seleção e validação completa')
        verificar(any(m['texto'] == '' for m in dados['sessoes'][0]['mensagens']),
                  'até respostas inválidas são preservadas')


if __name__ == '__main__':
    testar_regras()
    testar_persistencia_terminal()
    testar_api()
    print(f'\n{TOTAL} verificações aprovadas.')
