# Amostra de demonstração

`occurrences_sample.csv` é a amostra brasileira. Os arquivos com sufixos `ch`,
`ar` e `py` representam, respectivamente, Suíça, Argentina e Paraguai. São
amostras determinísticas para inspeção da estrutura e para o fallback público
do dashboard quando o PostgreSQL estiver indisponível. Cada arquivo contém no
máximo um registro por espécie e dez registros por dataset, limitado a
ocorrências com licença CC0 1.0 ou CC BY 4.0.

Cada linha mantém GBIF ID, dataset, organização publicadora, instituição, licença e links de referência. Para CC BY, a atribuição ao publicador original continua obrigatória.

A amostra não substitui um GBIF Occurrence Download com DOI e não deve ser usada como base integral para análise científica. Consulte `metadata.json` e `docs/CITACAO_E_LICENCAS.md`.
