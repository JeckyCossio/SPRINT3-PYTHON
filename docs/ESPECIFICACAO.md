# Especificação técnica — JOVI AI — Sprint 4

## 1. Objetivos e justificativa

A solução JOVI AI propõe reduzir a dificuldade de preparar uma câmera a partir da intenção de quem fotografa. O contexto da equipe destaca a persona Camila, estudante de 19 anos, e situações como slides ilegíveis, fotos de amigos à noite e perda de tempo em menus. Não se afirmam melhorias fotográficas medidas.

Nesta entrega, o objetivo é demonstrar esse preparo em um programa Python independente de terminal: o usuário escolhe categorias e informa a cena; funções determinísticas selecionam configurações simuladas compatíveis com um perfil fictício. A consulta real à Open-Meteo acrescenta contexto de planejamento de fotografias externas. JSON conserva as interações entre execuções.

O escopo foi ajustado pela equipe para uma implementação simples, sem IA e sem conexão ao protótipo web. O programa não executa a arquitetura futura multimodal/RAG, não detecta iluminação, não altera hardware e não analisa fotos depois do disparo. Somente a consulta externa e o armazenamento são integrações reais desta entrega.

## 2. Fluxos e funcionalidades

### Preparação automática simulada

Consentimento único → categoria → ambiente → luz → movimento → perfil fictício → clima opcional em ambiente externo → decisões por regras → resultado explicitamente simulado → menu.

Categorias: retrato de uma pessoa, grupo, documento impresso, slide projetado e paisagem. Ambiente: interno/externo. Luz: baixa, uniforme ou alto contraste. Movimento: sim/não. Perfis: completo (Foto, Retrato, Documento, Noturno e HDR) ou básico (somente Foto, sem HDR). Não são atribuídos esses recursos a um modelo comercial real.

Não se solicita confirmação de cada parâmetro. A pessoa pode cancelar com `/`. O fluxo termina antes de qualquer captura; a mensagem informa que, no produto proposto, o disparo pertence ao usuário.

### Consulta meteorológica

Nome da cidade → geolocalização Open-Meteo → seleção de cidade com estado/país → consulta atual e horários solares de hoje → saída com fonte e horários → menu. Pode ser iniciada de forma independente ou durante preparação externa. O programa não pede coordenadas ao usuário.

### Histórico

Registra integralmente perguntas, respostas, mensagens e resultados das preparações/consultas. Permite leitura de uma sessão, exclusão individual e exclusão total mediante confirmação. Operações administrativas de leitura/exclusão não criam novas sessões. Não há busca nem resumo de conversas.

## 3. Tabela de decisões

As regras são avaliadas na ordem abaixo. Slide e documento têm prioridade sobre regras genéricas de luz/movimento. O programa seleciona modo e prioridades qualitativas; não promete ajustes universais de ISO ou obturador.

| Prioridade | Condição | Decisão simulada | Justificativa/limite |
|---|---|---|---|
| 1 | Slide projetado | Foto; foco no texto; reduzir brilho; sem flash/HDR | Preservar áreas claras da projeção; não usar exposição noturna longa. |
| 2 | Documento impresso | Documento; foco no texto | Priorizar legibilidade, sem desfoque; alertar se houver pouca luz. |
| 3 | Demais assuntos em movimento | Foto; priorizar tempo curto e acompanhamento | Evitar borrões de exposição longa; pouca luz gera alerta de limitação. |
| 4 | Demais assuntos parados, pouca luz | Noturno | Priorizar captura em baixa luz; alertar sobre necessidade de estabilidade. |
| 5 | Retrato parado, luz suficiente | Retrato; foco no rosto | Destacar uma pessoa. |
| 6 | Grupo parado, luz suficiente | Foto; foco no grupo | Preservar as pessoas, sem desfoque de retrato. |
| 7 | Paisagem parada, luz suficiente | Foto; foco na cena ampla | Priorizar detalhes. |
| Complemento | Alto contraste, assunto parado, sem Noturno e sem texto | Ativar HDR, se suportado | Equilibrar contraste; não combinar com movimento, Noturno ou slide/documento. |
| Compatibilidade | Modo ausente no perfil | Usar Foto e explicar limitação | Nunca informar ativação de recurso inexistente. |
| Compatibilidade | HDR ausente no perfil | Manter HDR desativado e avisar | Respeitar o perfil fictício. |

O foco é ajustado para o grupo ou rosto quando pertinente. Flash permanece desativado: não existe automação de iluminação real. O ambiente externo oferece consulta opcional de clima; meteorologia não substitui a iluminação informada nem decide o modo fotográfico. A tabela deriva dos cenários da base JOVI, adaptados para esta simulação acadêmica, e não constitui orientação universal de fotografia.

## 4. Organização técnica e persistência

`main.py` controla execução e retorno ao menu. `funcoes.py` contém interação e casos de uso. `regras.py` recebe cenário/perfil e retorna um dicionário de configuração. `clima.py` recebe cidade, consome APIs e retorna dados ou erro. `persistencia.py` recebe dados/caminhos e lê/grava JSON. Funções trocam dados por parâmetros e retornos; não há classes ou estado global mutável de sessões.

Dependência externa: requests. Módulos nativos: json, pathlib, datetime e math. Os testes usam ainda tempfile, unittest.mock, contextlib, io e sys, todos nativos. Python mínimo 3.9. A aplicação usa somente chamadas HTTPS com verificação TLS padrão, timeout e tratamento de exceções.

Esquema do JSON: objeto com `versao: 1` e lista `sessoes`. Cada sessão contém `id`, `inicio`, `tipo`, `status`, `mensagens`, `resultado` e, quando finalizada, `fim`. Mensagens contêm `horario`, `papel` e `texto`. Status possíveis incluem em andamento, concluída, cancelada, interrompida, falha na API e cidade não encontrada. Uma interrupção abrupta pode deixar status em andamento no arquivo; ao carregar, passa a interrompida.

A gravação progressiva usa `dados/historico.tmp` e substitui `historico.json` somente após concluir a escrita. Arquivos inválidos são preservados e exigem correção/renomeação manual antes de continuar. Falha de gravação é informada; não há garantia de persistência se o sistema de arquivos negar acesso. O projeto é de usuário único e não suporta concorrência entre instâncias.

## 5. Contrato das APIs e uso de horários

Geolocalização: GET https://geocoding-api.open-meteo.com/v1/search com name, count=5, language=pt e format=json. O sistema valida nomes e coordenadas e solicita seleção do resultado.

Meteorologia: GET https://api.open-meteo.com/v1/forecast com latitude, longitude, current=temperature_2m,precipitation,cloud_cover,is_day; daily=sunrise,sunset; forecast_days=1; timezone=auto; timeformat=unixtime. As unidades padrão são °C, mm e %. Não são feitas chamadas a modelos de IA.

A data e hora dos registros e do menu são obtidas do sistema operacional, com fuso. O horário dos dados climáticos e o dia dos eventos solares correspondem à cidade consultada, com offset fornecido pela API. O resultado não é uma medição em tempo real da câmera. O horário do sistema é exibido junto ao clima e compara-se o instante atual ao pôr do sol para informar se já passou. Eventos solares nulos são indicados como indisponíveis.

Sem chave de API para uso gratuito não comercial, sujeito aos limites do provedor. Dados meteorológicos: Open-Meteo, CC BY 4.0. Geolocalização baseada no GeoNames, conforme documentação do serviço. O programa exibe crédito e mantém as URLs nesta documentação.

## 6. Validações e tratamento de exceções

Menus e perguntas aceitam somente opções previstas; entradas vazias ou inválidas geram nova tentativa. A cidade exige de 2 a 100 caracteres e ao menos uma letra. `/` cancela; EOF/Ctrl+C finalizam com segurança e registram a interrupção quando houver sessão ativa.

ConnectionError: provável falta de internet ou indisponibilidade. Timeout: demora e possível instabilidade. HTTPError: erro do serviço HTTP. JSON inválido, estrutura incompleta, valores fora de faixa ou coordenadas inválidas: mensagem específica, sem inventar dados. A preparação pode continuar sem meteorologia. A consulta independente registra a falha e retorna ao menu.

JSON corrompido, versão/estrutura incompatível e falha de escrita têm tratamento próprio. A exclusão só altera os dados em memória depois de salvar a nova versão com sucesso; confirmação recusada não modifica o histórico.

## 7. Evolução em relação à Sprint 3

Base analisada: main.py e funcoes.py da branch main, commit 5f59e40afb681dd5bbd727584a6784426db0bfb6. A implementação anterior tinha guia passo a passo, acionamento de modos, avaliação pós-foto com notas aleatórias e histórico somente em memória; o cabeçalho ainda dizia Sprint 2.

| Ação | Alteração | Justificativa |
|---|---|---|
| Removido | Guia passo a passo e confirmações de cada instrução | O escopo vigente é automático. |
| Removido | Avaliação/melhorias pós-foto e notas aleatórias | Estão fora do escopo e não constituíam análise real. |
| Modificado | Acionamento de modos virou preparação pré-captura por regras | Alinhar a intenção, cena informada e compatibilidade simulada. |
| Modificado | Histórico em memória passou a JSON persistente completo | Atender persistência e recuperar interações entre execuções. |
| Preservado/adaptado | Menu, repetição, validações, separação em funções e atalho / | Reaproveitar a base útil da Sprint anterior. |
| Modificado | Exceção personalizada de retorno substituída por retorno None | Atender à escolha de não usar classes. |
| Adicionado | Open-Meteo com geolocalização e meteorologia | Cumprir API externa real, vinculada à fotografia ao ar livre. |
| Adicionado | Perfis fictícios e fallback | Demonstrar verificação de capacidades sem inventar suporte de aparelhos. |
| Adicionado | Exclusão, tratamento de arquivos, testes, README e PDF | Robustez, facilidade de execução e atendimento da entrega. |
| Corrigido | Identificação para Sprint 4 | Corrigir rótulo antigo e documentar a evolução. |
| Retirado do versionamento da nova branch | .idea e __pycache__ | Entregar fontes e documentos, sem configuração local de IDE ou bytecode. |

A main é preservada; o trabalho está na branch sprint4, sem merge. Integração com disciplinas/web foi dispensada pela professora segundo orientação da equipe. O título Sprint 3 na segunda imagem é tratado como erro da professora confirmado pelo usuário: documentação e ZIP pertencem à Sprint 4.

## 8. Critérios e verificação

Programa (20 pontos): menu, coerência, retorno e saída. Implementação (50): funções, validações/try-except, JSON, API e clareza. Documentação (25): capa com projeto/integrantes/turma, sumário, objetivos/justificativa/funcionalidades e alterações. Entrega (5): ZIP único com PDF e código.

As verificações automatizadas cobrem as regras de decisão, 60 combinações de categoria/luz/movimento/perfil, leitura após reinício, histórico completo, exclusão confirmada/cancelada, JSON inválido, falha de gravação, menus e API com erros simulados. A chamada real à Open-Meteo foi testada separadamente. Consulte VALIDACAO.md para resultados e limites do ambiente de verificação.

## 9. Instalação, entrega e referências

Extrair o ZIP, instalar requirements.txt e executar main.py em Python 3.9+. O PDF já está gerado; não há ferramenta adicional de documentação a instalar. Internet é exigida somente para a API. O pacote não contém histórico pessoal, ambiente virtual, .idea nem __pycache__.

Referências: duas imagens de requisitos de Computational Thinking with Python fornecidas pela equipe; JOVI_BASE_CONHECIMENTO_COMPLETA.md (versão 1.0, 21/10/2026), especialmente seções 2, 3, 5 a 8; código da Sprint 3 no commit identificado na seção 7; decisões da equipe nesta construção sobre API, simplicidade, formato e dispensa de integração; https://open-meteo.com/en/docs ; https://open-meteo.com/en/docs/geocoding-api ; https://open-meteo.com/en/terms ; https://creativecommons.org/licenses/by/4.0/ ; https://www.geonames.org/ .
