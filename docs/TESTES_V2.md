# Testes da versão 2

## Execução

Instale as dependências de desenvolvimento e execute a suíte:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

O arquivo `pytest.ini` limita a descoberta à pasta `tests/`. Os testes continuam
escritos com `unittest`, portanto podem ser executados tanto pelo pytest quanto
diretamente pela biblioteca padrão.

## Matriz da Etapa 11

| Requisito | Evidência automatizada |
|---|---|
| Consulta taxonômica | correspondência de espécie, chave ausente, consulta SQL parametrizada e hierarquia aceita |
| Paginação | múltiplas páginas, limite total, tamanho de página e limite da API de busca |
| Datas em formatos diferentes | datas simples, timestamps e precisão mensal normalizados |
| Coordenadas | pontos internos, externos, sobre o limite, reprojeção, valores nulos e inválidos |
| Remoção de duplicidades | GBIF ID repetido removido antes da carga e chave repetida rejeitada na preparação |
| Inserção no PostgreSQL | upserts e importações verificados com conexão falsa e transação real reversível |
| Atualização sem duplicação | a mesma carga é executada duas vezes e mantém uma ocorrência por `gbif_key` |
| API indisponível | timeout, falha de conexão e HTTP 503 convertidos em `ErroGBIF` claro |
| País sem resultados | sincronização interrompida antes de escrever arquivos ou alterar o cache; dashboard exibe aviso |
| Filtros do dashboard | combinação unitária e interação Streamlit para espécie, origem, período, tipo e unidade administrativa |

## PostgreSQL real

Por segurança, o teste de integração só roda quando `TEST_DATABASE_URL` está
definida. Ele cria a estrutura dentro de uma transação, executa a carga duas
vezes, verifica relacionamentos e idempotência e faz `rollback` ao final.

Para usar a conexão já configurada em `.env` no PowerShell:

```powershell
$databaseLine = Get-Content .env |
    Where-Object { $_ -match '^DATABASE_URL=' } |
    Select-Object -First 1
$env:TEST_DATABASE_URL = $databaseLine.Substring('DATABASE_URL='.Length)
python -m pytest tests/test_load.py -v
```

## Pipeline

A integração contínua instala `requirements-dev.txt`, verifica lint e
formatação com Ruff e executa `python -m pytest -v`. Falhas de serviços externos
são simuladas; a suíte comum não depende da disponibilidade da API do GBIF.
