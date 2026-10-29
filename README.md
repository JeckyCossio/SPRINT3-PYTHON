# JOVI AI — Sprint 4 de Python

**Equipe:** Open Source Consulting · **Turma:** 1 ESPI  
**Disciplina:** Computational Thinking with Python · **Entrega:** 03/11/2026

Protótipo acadêmico de terminal para preparar **configurações fotográficas simuladas antes da captura**, com decisões por regras, consulta real à Open-Meteo e histórico em JSON. Não utiliza IA, classes, câmera, voz, Flask ou FastAPI. Não depende do projeto web.

## Integrantes

| Integrante | RM |
|---|---|
| Daniel Roberto Ribeiro de Figueiredo | 571746 |
| Felipe Rossano Pedrol | 569631 |
| Felipi Bandeira de Godoy | 573741 |
| Jecky Cossio | 572226 |
| Leonardo Ferreira Barbosa | 571311 |

## Executar no Windows / PyCharm

1. Instale Python **3.9 ou superior** e extraia todo o ZIP para uma pasta gravável.
2. No PyCharm, abra a pasta e selecione um interpretador Python. Se desejar, use o ambiente virtual que o próprio PyCharm oferece.
3. No terminal dessa pasta, execute:

```console
python -m pip install -r requirements.txt
python main.py
```

No Windows, se o comando `python` não estiver disponível, experimente `py -3` no lugar de `python`. Use o mesmo interpretador para instalar as dependências e executar o programa. No PyCharm, também pode executar `main.py` pelo botão Run.

A única dependência externa do aplicativo é **requests**. Não é necessária chave de API. Internet é necessária para consultar cidades e clima; a preparação simulada e o histórico funcionam sem internet. Os caminhos são relativos à localização dos arquivos Python, independentemente da pasta de trabalho do PyCharm.

## Menu e roteiro rápido

- **1 — Preparação automática simulada:** autorize a simulação, escolha o assunto, ambiente, iluminação, movimento e perfil de recursos. Em ambiente externo, a consulta ao clima é opcional.
- **2 — Condições para fotografia externa:** digite uma cidade, selecione o resultado com estado/país e consulte clima e horários solares de hoje.
- **3 — Sessões anteriores:** escolha uma sessão para ler todas as perguntas, respostas e mensagens do fluxo.
- **4 — Excluir histórico:** escolha uma sessão ou `T` para todas. Confirme com `s`; `n` ou `/` cancela.
- **0 — Sair.** Durante os fluxos, `/` cancela e retorna ao menu. Ctrl+C ou fim de entrada encerra com segurança.

Exemplo sem internet: opção 1 → autorizar 1 → grupo 2 → interno 1 → pouca luz 1 → em movimento 1 → perfil completo 1. O resultado simulado usa Foto e evita exposição longa por causa do movimento. Depois, o programa retorna ao menu.

Não há prompt de IA: assuntos e condições são escolhidos em categorias. Apenas o nome da cidade é digitado livremente para a geolocalização.

## Regras e limites

As regras refletem os cenários do projeto: slide projetado, documento, retrato, grupo e paisagem. Consulte [a documentação técnica](docs/ESPECIFICACAO.md) e [o PDF](docs/JOVI_AI_Sprint4_Documentacao.pdf).

- Preparação exclusivamente **pré-captura e automática simulada**, sem tutorial de ajuste manual ou análise pós-foto.
- Perfis completo/básico são **fictícios**, não especificações de um aparelho JOVI. Recursos indisponíveis usam alternativa Foto e mensagem explícita.
- Não há captura de imagens, RAG ou IA; o contexto é fornecido pelo usuário.
- Meteorologia não mede a iluminação da cena. O clima não substitui a resposta sobre luz e não aciona modos de câmera.
- Não são atribuídos ISO, velocidade ou configurações universais sem conhecer hardware. O programa escolhe modos e prioridades qualitativas.
- Nenhuma configuração real é alterada e nenhuma foto é disparada.

## Open-Meteo e horários

Geolocalização: `https://geocoding-api.open-meteo.com/v1/search`. Meteorologia: `https://api.open-meteo.com/v1/forecast`.

A primeira consulta converte o nome da cidade em coordenadas e lista até cinco resultados com estado/país. A segunda usa `current` para temperatura, precipitação, nebulosidade e dia/noite; `daily` para nascer/pôr do sol; `forecast_days=1`, `timezone=auto` e timestamps Unix.

O menu e os registros usam **a data, hora e fuso atuais do sistema operacional**, sem data fixa. A API fornece condições atuais do modelo e horários solares do dia local da cidade. O horário dos dados é exibido separadamente: não representa medição instantânea nem necessariamente coincide com o relógio do computador. Um aviso informa se o pôr do sol de hoje já passou. Horários solares ausentes são exibidos como indisponíveis.

As requisições têm timeout de 10 segundos cada. Falhas de conexão indicam provável falta de internet ou indisponibilidade do serviço; timeout, HTTP e conteúdo inválido têm mensagens próprias. Uma preparação pode continuar sem clima; nunca se inventam dados de previsão.

**Crédito:** dados meteorológicos por [Open-Meteo](https://open-meteo.com/), licença [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). A geolocalização usa dados do [GeoNames](https://www.geonames.org/), conforme documentação da Open-Meteo. Serviço gratuito destinado a uso não comercial, sujeito às condições e limites do provedor.

## Histórico e exclusão

O programa cria automaticamente `dados/historico.json` e salva progressivamente perguntas, respostas (inclusive inválidas), mensagens, horários, status e resultado de cada preparação/consulta. Não resume conversas nem armazena imagens. `/`, recusa e interrupção são registrados na sessão. Uma sessão deixada em andamento por encerramento abrupto é identificada como interrompida ao carregar.

Leitura e exclusão do histórico são operações administrativas: não criam novas sessões, para evitar duplicações e permitir que a exclusão total deixe o histórico vazio. O número do menu que iniciou cada preparação/consulta também integra seu registro.

A escrita usa arquivo temporário e substituição após a gravação completa. Arquivo corrompido ou estrutura incompatível impede a abertura do programa e é preservado: faça uma cópia e corrija/renomeie o arquivo antes de reiniciar. Erros de gravação geram aviso; dados podem permanecer apenas em memória até nova gravação bem-sucedida. Não execute duas instâncias sobre o mesmo histórico simultaneamente.

## Arquivos

```text
main.py              Menu principal e execução
funcoes.py           Perguntas, respostas, histórico e fluxo de preparação
regras.py            Tabela de decisões e perfis simulados
clima.py             Requisições e validação da Open-Meteo
persistencia.py      JSON, datas e registros
requirements.txt     Única dependência externa: requests
docs/                Especificação, PDF e relatório de validação
tests/verificar.py   Verificações automatizadas sem classes
dados/               Criada na primeira gravação; histórico local não versionado
```

## Verificações

```console
python tests/verificar.py
```

Os testes usam recursos nativos do Python e `requests`, sem instalar bibliotecas adicionais. Verificam regras, navegação, cancelamento, histórico, exclusão e falhas de API simuladas. A consulta real foi verificada separadamente; consulte [VALIDACAO.md](docs/VALIDACAO.md). Não foi executado teste nativo no Windows nesta construção; foram usados caminhos portáveis e instruções para Windows/PyCharm.

## Entrega e evolução

Entregar via Teams **um único ZIP contendo PDF e código-fonte**. README, testes e especificação são complementos. Não é necessário instalar ferramentas para gerar PDF: ele já está pronto.

A branch `sprint4` evolui a Sprint 3; a `main` permanece como referência da versão anterior, sem merge automático. Foram retirados modo guiado, feedback pós-foto e notas aleatórias; foram acrescentados regras pré-captura, API real, JSON e documentação. A integração com outras disciplinas foi dispensada pela professora, conforme orientação informada pela equipe nesta construção. Persistência JSON não é apresentada como integração web.
