# Comparação entre países

## Objetivo

A Etapa 9 permite comparar dois países sem tratar contagens publicadas como
medida direta de abundância ou biodiversidade. Brasil e Suíça são a seleção
inicial, mas qualquer par com dados armazenados pode ser escolhido.

## Métricas apresentadas

- ocorrências e espécies registradas;
- período e quantidade de anos com registros;
- registros por espécie, usado apenas como indicador descritivo da amostra;
- percentual de registros com data e coordenadas válidas;
- ocorrências anuais brutas;
- percentual anual dentro da amostra de cada país;
- espécies compartilhadas e exclusivas;
- similaridade de Jaccard entre os conjuntos de espécies.

A série normalizada é calculada por:

```text
percentual do ano = ocorrências do país no ano / ocorrências com ano no país × 100
```

Os percentuais de cada país somam 100%. Essa transformação permite comparar a
distribuição temporal interna, mas não iguala esforço de amostragem.

## Espécies compartilhadas e exclusivas

A comparação usa a chave taxonômica aceita do Catalogue of Life. Uma espécie é:

- compartilhada quando a mesma chave ocorre nos dois conjuntos;
- exclusiva quando a chave ocorre somente em uma das amostras selecionadas.

“Exclusiva” significa exclusiva da amostra consultada, não endêmica nem ausente
do outro país. Resultados podem mudar com novas coletas e publicações.

## Resultado atual Brasil–Suíça

Na carga validada em 26 de julho de 2026:

| Métrica | Brasil | Suíça |
| --- | ---: | ---: |
| Ocorrências aproveitadas | 3.764 | 4.802 |
| Espécies registradas | 352 | 61 |
| Registros por espécie | 10,7 | 78,7 |
| Anos com registros | 7 | 5 |
| Período | 2020–2026 | 2022–2026 |

Foram encontradas 5 espécies compartilhadas, 347 exclusivas da amostra
brasileira e 56 exclusivas da amostra suíça. A similaridade de Jaccard é 1,2%.

## Cuidado metodológico

Mais registros ou mais espécies registradas não demonstram, isoladamente,
maior abundância ou biodiversidade. As diferenças também dependem de:

- tamanho e heterogeneidade da área;
- cobertura temporal;
- intensidade e desenho do esforço de coleta;
- instituições e projetos participantes;
- digitalização e frequência de publicação no GBIF;
- truncamento das amostras interativas em até 5.000 registros recebidos.

Inferências ecológicas exigem downloads integrais com DOI e métodos que controlem
explicitamente esforço, detectabilidade e cobertura espacial e temporal.

## Testes

Os testes automatizados verificam contagens, normalização temporal, espécies
compartilhadas, exclusivas, índice de Jaccard, rejeição de países iguais e
renderização da comparação no dashboard.
