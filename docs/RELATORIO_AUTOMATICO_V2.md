# Relatório automático

## Objetivo

A Etapa 10 permite baixar um PDF reproduzível do recorte ativo no dashboard. O
relatório usa o país, as espécies e o período selecionados, além dos filtros de
origem, tipo de registro e unidade administrativa.

## Conteúdo do PDF

O documento possui três páginas:

1. resumo da consulta, filtros, indicadores de cobertura, metodologia e
   limitações;
2. ranking de espécies, distribuição anual e espécies por origem;
3. mapa dos registros com coordenadas válidas.

Cada página informa o país, a fonte ativa e a data e hora de geração. A primeira
página também contém uma assinatura de 16 caracteres calculada a partir dos
GBIF IDs ordenados. A mesma seleção de registros produz a mesma assinatura,
independentemente da ordem das linhas.

## Como gerar

1. Abra o dashboard e escolha o país.
2. Selecione uma ou várias espécies, ou mantenha todas.
3. Ajuste o período e os demais filtros.
4. Abra a aba **Relatório**.
5. Confira o resumo e use **Baixar relatório PDF**.

O arquivo é produzido localmente pela aplicação e não envia os dados a um
serviço externo.

## Reprodutibilidade

Para reproduzir uma consulta, use a mesma fonte de dados, reaplique todos os
filtros listados no PDF e compare a assinatura. Uma assinatura diferente indica
que o conjunto de GBIF IDs mudou, por atualização da fonte ou por diferença nos
filtros.

## Limitações

O relatório resume ocorrências publicadas e não estima abundância, ocupação ou
biodiversidade real. Diferenças de esforço de coleta, período, área e publicação
afetam as contagens. Pontos sobrepostos no mapa podem ocultar concentrações, e
registros sem coordenadas válidas não aparecem na página espacial. A fonte ativa
pode representar apenas uma amostra dos resultados disponíveis no GBIF.
