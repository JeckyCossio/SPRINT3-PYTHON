"""Regras determinísticas pré-captura: não há IA nem controle de câmera."""
CATEGORIAS = {
    '1': 'Retrato de uma pessoa', '2': 'Grupo de pessoas',
    '3': 'Documento impresso', '4': 'Slide projetado', '5': 'Paisagem',
}
PERFIS = {
    '1': {'nome': 'Completo (simulado)',
          'modos': ['Foto', 'Retrato', 'Documento', 'Noturno'], 'hdr': True},
    '2': {'nome': 'Básico (simulado)', 'modos': ['Foto'], 'hdr': False},
}


def decidir_configuracao(cenario, perfil):
    """Combina categoria, luz e movimento e verifica capacidades simuladas.

    HDR é um recurso separado do modo. Não combinamos HDR com Noturno,
    movimento ou slide. Não inventamos valores universais de ISO/exposição.
    """
    categoria = cenario['categoria']
    pouca_luz = cenario['luz'] == 'baixa'
    movimento = cenario['movimento'] == 'sim'
    motivos = []
    avisos = []
    hdr = False
    foco = 'automático'
    exposicao = 'automática'
    modo = 'Foto'

    if categoria == '4':
        foco = 'texto do slide'
        exposicao = 'reduzir brilho para preservar o texto projetado'
        motivos.append('Slide: priorizar legibilidade e preservar áreas claras.')
        avisos.append('Flash desativado: não ilumina a projeção e pode atrapalhar.')
    elif categoria == '3':
        modo = 'Documento'
        foco = 'texto do documento'
        motivos.append('Documento: priorizar texto nítido, sem desfoque de retrato.')
        if pouca_luz:
            avisos.append('Pouca luz pode limitar a legibilidade do documento.')
    elif movimento:
        foco = 'acompanhamento do assunto (simulado)'
        exposicao = 'priorizar tempo curto, dentro do suporte do dispositivo'
        motivos.append('Movimento: evitar exposição longa para reduzir borrões.')
        if pouca_luz:
            avisos.append('Movimento com pouca luz: nitidez e ruído podem ficar limitados.')
    elif pouca_luz:
        modo = 'Noturno'
        motivos.append('Cena parada e pouca luz: priorizar modo noturno, se disponível.')
        avisos.append('Exposição prolongada depende de estabilidade e pode gerar borrões.')
    elif categoria == '1':
        modo = 'Retrato'
        foco = 'rosto principal'
        motivos.append('Retrato com luz suficiente: destacar uma pessoa.')
    elif categoria == '2':
        foco = 'grupo de rostos'
        motivos.append('Grupo: preservar as pessoas em foco, sem desfoque de retrato.')
    else:
        foco = 'cena ampla'
        motivos.append('Paisagem: priorizar detalhes da cena.')

    if categoria == '2':
        foco = 'grupo de rostos'
    if categoria == '1' and not movimento:
        foco = 'rosto principal'
    if (cenario['luz'] == 'contraste' and not movimento
            and modo != 'Noturno' and categoria not in ('3', '4')):
        hdr = True
        motivos.append('Alto contraste em cena parada: considerar HDR.')
    if modo not in perfil['modos']:
        avisos.append(f'Modo {modo} indisponível no perfil; alternativa: Foto.')
        modo = 'Foto'
    if hdr and not perfil['hdr']:
        hdr = False
        avisos.append('HDR indisponível no perfil; exposição automática mantida.')
    return {'modo': modo, 'hdr': hdr, 'foco': foco, 'exposicao': exposicao,
            'flash': 'desativado', 'motivos': motivos, 'avisos': avisos,
            'simulado': True, 'perfil': perfil['nome']}
