# Relatório de validação — Sprint 4

Data: 28/10/2026. Ambiente: Linux, Python 3.12. O aplicativo foi projetado para Python 3.9+ e Windows/PyCharm; não houve execução nativa no Windows.

## Verificações automatizadas

Comando: `python tests/verificar.py`.

**Resultado: 36 verificações aprovadas**, incluindo avaliação de 60 combinações de categoria, luz, movimento e perfil de recursos.

Cobertura: decisões pré-captura e compatibilidade; menu inválido; retorno e saída; preparação completa; perguntas e respostas em JSON; recuperação após reinício; cancelamento por /; recusa do consentimento; Ctrl+C; falha da API sem bloquear preparação; exclusão individual e total; cancelamento de exclusão; JSON corrompido preservado; estrutura inválida; falha de gravação; conexão, timeout, HTTP e JSON inválido; cidade inexistente; coordenadas incompletas; dados meteorológicos incompletos; relógios separados; seleção de cidade e registro de respostas inválidas.

Os erros da API são reproduzidos por mocks locais, sem depender de uma falha real do provedor. Os testes não usam classes ou bibliotecas externas adicionais.

## Consumo real de API

Consulta real em 28/10/2026: geolocalização de São Paulo, seleção da cidade e requisição de condições atuais/horários solares. Verificados separadamente do teste com mocks.

Também foi executado o fluxo completo do terminal com a API real, incluindo menu, seleção, exibição, armazenamento da transcrição e retorno ao menu. O horário do sistema e o horário local da cidade aparecem separados. Os dados são variáveis e não devem ser comparados a valores fixos de temperatura em avaliações futuras.

## Pacote e documentação

PDF conferido por extração de texto e inspeção visual de páginas representativas. O ZIP contém documentação PDF, fontes, README, dependências e testes. Exclui histórico pessoal, .idea, __pycache__, ambientes virtuais e arquivos temporários. A extração em pasta limpa foi seguida por instalação das dependências e execução das verificações e do ponto de entrada.

## Limites

Não foram testados controle de câmera, IA, imagens ou integração web: estão fora do escopo implementado. Os perfis de câmera são fictícios. Não há medição de melhora de fotografia nem promessa de desempenho. Não foi realizado teste nativo no Windows. API requer internet e está sujeita à disponibilidade/limites do serviço. Execute uma instância por vez para evitar concorrência no histórico.
