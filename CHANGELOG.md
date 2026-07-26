# Changelog

Todas as alterações relevantes deste projeto são documentadas neste arquivo.

## [Não publicado]

### Adicionado

- dashboard global por país com fonte e última atualização;
- mapas de pontos por espécie, calor e agrupamento espacial;
- detalhe selecionável de ocorrência;
- séries anual, mensal e comparação temporal entre espécies;
- catálogo taxonômico pesquisável e filtros globais de período e localização.
- comparação entre dois países com métricas brutas e normalizadas;
- identificação de espécies compartilhadas e exclusivas por país;
- aviso metodológico sobre esforço amostral e vieses de publicação.
- relatório PDF reproduzível a partir dos filtros ativos;
- gráficos, mapa, metodologia, limitações, fonte, data e assinatura dos
  registros incluídos no relatório.

## [1.0.0] - 2026-07-16

### Adicionado

- extração paginada e configurável da API GBIF;
- recorte oficial da porção brasileira da Região Hidrográfica do Paraná;
- coleta multiespécies e taxonomia Catalogue of Life;
- classificação conservadora de origem;
- análise exploratória espacial, temporal e de qualidade;
- banco PostgreSQL com carga idempotente e views;
- dashboard Streamlit responsivo;
- preservação de licenças e amostra pública CC0/CC BY;
- logging configurável, Ruff e integração contínua;
- documentação de arquitetura, citação e reprodução.

### Dados da execução

- 5.000 registros brutos na amostra da API;
- 3.792 ocorrências dentro da bacia;
- 356 espécies distintas;
- 555 registros taxonomicamente imprecisos separados para auditoria.

### Limitações

- a consulta completa possui mais de 100.000 resultados e exige GBIF Occurrence Download com DOI;
- as contagens representam registros publicados, não abundância biológica;
- a classificação de origem permanece desconhecida sem evidência explícita.
