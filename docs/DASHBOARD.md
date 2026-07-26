# Dashboard Streamlit

## Visão geral

A Etapa 8 disponibiliza uma interface global para explorar ocorrências de peixes
por país. O dashboard consulta o schema PostgreSQL `biodiversity` e usa os CSVs
processados como fallback quando a conexão não está disponível.

## Execução

Instale as dependências e inicie o servidor:

```powershell
pip install -r requirements.txt
streamlit run app/app.py
```

Por padrão, a aplicação fica disponível em `http://localhost:8501`.

## Componentes

### Filtros

- país;
- espécie;
- classificação de origem;
- intervalo anual;
- tipo de registro;
- unidade administrativa informada.

Todos os indicadores e elementos visuais usam simultaneamente o mesmo recorte.

### Visão geral

- quantidade de ocorrências;
- espécies distintas;
- período coberto;
- data da última atualização;
- fonte ativa;
- espécies introduzidas;
- ranking das espécies;
- distribuição das espécies por origem.

### Mapa

O mapa usa PyDeck e oferece três modos: pontos coloridos por espécie, mapa de
calor e agrupamento espacial hexagonal. O usuário pode selecionar um GBIF ID
para consultar espécie, taxonomia, data, tipo, localidade e coordenadas. Para o
Brasil, o limite oficial simplificado é exibido apenas como referência visual.

### Temporal

A aba apresenta ocorrências por ano, série mensal e comparação anual entre as
cinco espécies mais registradas no recorte. O filtro de período da barra lateral
é aplicado simultaneamente a todas as séries.

### Espécies

O catálogo taxonômico apresenta chave aceita, nome científico, família, ordem,
número de ocorrências, origem e categoria IUCN. A busca aceita fragmentos do
nome científico sem expressão regular. O ranking e a comparação temporal usam
os mesmos filtros globais.

### Comparação

A aba permite selecionar dois países, começando por Brasil e Suíça. Ela compara
ocorrências, espécies, cobertura temporal, registros por espécie e completude
de data e coordenadas. As séries anuais são exibidas em contagens brutas e como
percentual da amostra de cada país. Tabelas separam espécies compartilhadas e
exclusivas e informam a similaridade de Jaccard.

A normalização facilita comparar o formato temporal das amostras, mas não
elimina diferenças de área, esforço de coleta, instituições ou publicação.

### Relatório

A aba gera um PDF de três páginas a partir do recorte global ativo. O documento
inclui resumo e filtros, indicadores, gráficos, mapa, metodologia, limitações,
fonte e data de geração. Uma assinatura derivada dos GBIF IDs permite verificar
se duas execuções utilizaram o mesmo conjunto de registros.

O PDF é criado localmente e pode ser baixado sem transmitir os dados para um
serviço externo. Consulte [Relatório automático](RELATORIO_AUTOMATICO_V2.md)
para o procedimento de reprodução.

### Qualidade

A aba apresenta o funil da última carga, o percentual aproveitado, registros sem
identificação válida no nível de espécie, datas ausentes ou apenas mensais,
coordenadas ausentes ou inválidas, duplicidades potenciais, alertas do GBIF e
registros potencialmente fora do país. Também detalha precisão das datas,
distribuição por tipo de evidência e frequências dos códigos de alerta.

### Dados

A tabela permite buscar por espécie, localidade ou unidade administrativa e exportar o recorte atual em CSV.

## Fonte de dados

A aplicação procura `DATABASE_URL` e `DB_SCHEMA` no ambiente ou no arquivo `.env`. Se o PostgreSQL falhar, tenta carregar:

- `data/processed/ocorrencias_peixes_bacia_parana.csv`;
- `data/processed/especies_bacia_parana.csv`.

A interface informa qual fonte está ativa e nunca exibe a URL de conexão.

## Publicação

Em uma hospedagem Streamlit, configure `DATABASE_URL` e `DB_SCHEMA` como secrets ou variáveis de ambiente. O banco precisa aceitar conexões da hospedagem. Os CSVs processados não são versionados e, portanto, não devem ser considerados fonte de produção sem uma etapa explícita de publicação dos dados.

## Validação

O dashboard foi validado com os 3.764 registros e 352 espécies do Brasil no
PostgreSQL:

- renderização sem exceções pelo framework de testes do Streamlit;
- filtros combinados testados com dados sintéticos;
- seleção de Brasil e Suíça validada contra o banco;
- pontos por espécie, mapa de calor e agrupamento espacial renderizados;
- séries anual, mensal e comparação entre espécies testadas;
- busca taxonômica, detalhe de ocorrência e comparação Brasil–Suíça disponíveis
  sem alterar código;
- funil da carga e indicadores de qualidade conferidos com o PostgreSQL.
- relatório PDF gerado com três páginas e assinatura estável dos registros.

As contagens representam ocorrências publicadas, não abundância biológica. A amostra atual também não substitui o download integral do GBIF com DOI.
