"""Leitura e gravação do histórico, sem classes ou dependências externas."""
import json
from datetime import datetime
from pathlib import Path

ARQUIVO_HISTORICO = Path(__file__).resolve().parent / 'dados' / 'historico.json'


def agora():
    """Data/hora local e fuso do sistema que executa o programa."""
    return datetime.now().astimezone().isoformat(timespec='seconds')


def novo_historico():
    return {'versao': 1, 'sessoes': []}


def validar_historico(dados):
    if not isinstance(dados, dict) or dados.get('versao') != 1:
        return False
    sessoes = dados.get('sessoes')
    if not isinstance(sessoes, list):
        return False
    ids = set()
    for sessao in sessoes:
        if not isinstance(sessao, dict):
            return False
        if not all(isinstance(sessao.get(c), str) for c in
                   ('id', 'inicio', 'tipo', 'status')):
            return False
        if sessao['id'] in ids:
            return False
        ids.add(sessao['id'])
        mensagens = sessao.get('mensagens')
        if not isinstance(mensagens, list):
            return False
        for mensagem in mensagens:
            if not isinstance(mensagem, dict) or not all(
                isinstance(mensagem.get(c), str)
                for c in ('horario', 'papel', 'texto')
            ):
                return False
    return True


def carregar_historico(caminho=ARQUIVO_HISTORICO):
    """Retorna (dados, erro). Arquivo inválido nunca é substituído."""
    try:
        dados = json.loads(Path(caminho).read_text(encoding='utf-8'))
        if not validar_historico(dados):
            raise ValueError('estrutura de histórico incompatível')
        # Uma interrupção abrupta pode deixar uma sessão sem finalização.
        for sessao in dados['sessoes']:
            if sessao['status'] == 'em andamento':
                sessao['status'] = 'interrompida'
        return dados, None
    except FileNotFoundError:
        return novo_historico(), None
    except (OSError, ValueError) as erro:
        return None, f'Não foi possível ler o histórico: {erro}'


def salvar_historico(dados, caminho=ARQUIVO_HISTORICO):
    """Grava em temporário e substitui somente após a escrita completa."""
    caminho = Path(caminho)
    temporario = caminho.with_suffix('.tmp')
    try:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        temporario.write_text(
            json.dumps(dados, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        temporario.replace(caminho)
        return None
    except OSError as erro:
        return f'Não foi possível salvar o histórico: {erro}. Dados mantidos em memória.'


def criar_sessao(dados, tipo):
    # Microssegundos evitam colisões entre sessões iniciadas no mesmo segundo.
    identificador = datetime.now().astimezone().isoformat(timespec='microseconds')
    sessao = {'id': identificador, 'inicio': agora(), 'tipo': tipo,
              'status': 'em andamento', 'mensagens': [], 'resultado': None}
    dados['sessoes'].append(sessao)
    return sessao


def registrar(sessao, papel, texto):
    sessao['mensagens'].append(
        {'horario': agora(), 'papel': papel, 'texto': str(texto)}
    )


def excluir_sessoes(dados, identificador=None):
    """Retorna uma cópia sem a sessão escolhida, ou sem todas as sessões."""
    return {'versao': dados['versao'], 'sessoes': [
        s for s in dados['sessoes']
        if identificador is not None and s['id'] != identificador
    ]}
