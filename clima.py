"""Consumo real da Open-Meteo; não analisa imagens nem mede a luz da cena."""
from datetime import datetime, timezone
from math import isfinite
import requests

URL_CIDADES = 'https://geocoding-api.open-meteo.com/v1/search'
URL_CLIMA = 'https://api.open-meteo.com/v1/forecast'
TIMEOUT = 10


def obter_json(url, parametros):
    """Retorna (resposta, erro), sem confundir falha HTTP com falta de internet."""
    try:
        resposta = requests.get(url, params=parametros, timeout=TIMEOUT)
        resposta.raise_for_status()
        dados = resposta.json()
        if not isinstance(dados, dict) or dados.get('error'):
            return None, 'A API Open-Meteo retornou uma resposta inválida ou erro de consulta.'
        return dados, None
    except requests.exceptions.Timeout:
        return None, ('A API Open-Meteo demorou para responder. Possível instabilidade '
                      'da internet ou do serviço. Tente novamente mais tarde.')
    except requests.exceptions.ConnectionError:
        return None, ('Erro ao acessar a API Open-Meteo: provável falta de internet '
                      'ou indisponibilidade do serviço.')
    except requests.exceptions.HTTPError:
        return None, 'A API Open-Meteo retornou um erro HTTP. Tente novamente mais tarde.'
    except ValueError:
        return None, 'A API Open-Meteo retornou dados que não são JSON válido.'
    except requests.exceptions.RequestException:
        return None, 'Não foi possível concluir a consulta à API Open-Meteo.'


def numero(valor):
    return (isinstance(valor, (int, float)) and not isinstance(valor, bool)
            and isfinite(valor))


def buscar_cidades(nome):
    dados, erro = obter_json(URL_CIDADES, {
        'name': nome, 'count': 5, 'language': 'pt', 'format': 'json'
    })
    if erro:
        return None, erro
    cidades = dados.get('results', [])
    if not isinstance(cidades, list):
        return None, 'A API retornou uma lista de cidades inválida.'
    validas = [c for c in cidades if isinstance(c, dict)
               and isinstance(c.get('name'), str)
               and numero(c.get('latitude')) and -90 <= c['latitude'] <= 90
               and numero(c.get('longitude')) and -180 <= c['longitude'] <= 180]
    if cidades and not validas:
        return None, 'A API não retornou coordenadas válidas para as cidades.'
    return validas, None


def nome_cidade(cidade):
    return ', '.join(str(cidade[c]) for c in ('name', 'admin1', 'country')
                     if cidade.get(c))


def consultar_clima(cidade):
    dados, erro = obter_json(URL_CLIMA, {
        'latitude': cidade['latitude'], 'longitude': cidade['longitude'],
        'current': 'temperature_2m,precipitation,cloud_cover,is_day',
        'daily': 'sunrise,sunset', 'forecast_days': 1,
        'timezone': 'auto', 'timeformat': 'unixtime',
    })
    if erro:
        return None, erro
    try:
        atual = dados['current']
        valores = [atual[c] for c in
                   ('time', 'temperature_2m', 'precipitation', 'cloud_cover', 'is_day')]
        nascer, por = dados['daily']['sunrise'][0], dados['daily']['sunset'][0]
        offset = dados['utc_offset_seconds']
        if not all(numero(v) for v in valores + [offset]):
            raise ValueError('valores inválidos')
        if not (0 <= atual['cloud_cover'] <= 100 and atual['precipitation'] >= 0
                and atual['is_day'] in (0, 1)):
            raise ValueError('faixa inválida')
        if any(v is not None and not numero(v) for v in (nascer, por)):
            raise ValueError('horário solar inválido')
        # Verifica também limites de timestamp antes de exibir ou salvar sucesso.
        for valor in [atual['time']] + [v for v in (nascer, por) if v is not None]:
            datetime.fromtimestamp(valor + offset, timezone.utc)
        return {'cidade': nome_cidade(cidade), 'atual': atual,
                'nascer': nascer, 'por': por, 'offset': offset,
                'fuso': str(dados['timezone']), 'fonte': 'Open-Meteo'}, None
    except (KeyError, TypeError, IndexError, ValueError, OverflowError, OSError):
        return None, 'A API Open-Meteo retornou dados meteorológicos incompletos ou inválidos.'


def horario_cidade(timestamp, offset):
    if timestamp is None:
        return 'indisponível para esta data/localidade'
    return datetime.fromtimestamp(timestamp + offset, timezone.utc).strftime('%d/%m/%Y %H:%M')


def formatar_clima(dados):
    atual = dados['atual']
    linhas = [
        f"Cidade: {dados['cidade']}",
        f"Horário do sistema: {datetime.now().astimezone().strftime('%d/%m/%Y %H:%M:%S %z')}",
        f"Horário dos dados na cidade: {horario_cidade(atual['time'], dados['offset'])} ({dados['fuso']})",
        f"Temperatura: {atual['temperature_2m']} °C",
        f"Precipitação atual: {atual['precipitation']} mm",
        f"Nebulosidade: {atual['cloud_cover']}%",
        f"Nascer do sol: {horario_cidade(dados['nascer'], dados['offset'])}",
        f"Pôr do sol: {horario_cidade(dados['por'], dados['offset'])}",
        'Fonte: Open-Meteo — https://open-meteo.com/ (CC BY 4.0).',
        'Dados meteorológicos são estimativas do modelo, não leitura da câmera.',
    ]
    if atual['precipitation'] > 0:
        linhas.append('Chuva indicada: considere um local coberto para fotografar.')
    if atual['is_day'] == 0:
        linhas.append('O modelo indica noite na cidade. Informe a iluminação real da cena.')
    if dados['por'] is not None and dados['por'] < datetime.now(timezone.utc).timestamp():
        linhas.append('O pôr do sol de hoje já passou nessa cidade.')
    return '\n'.join(linhas)
