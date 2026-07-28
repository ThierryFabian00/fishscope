# Publicação da versão 2

Dashboard público: <https://biodiversidade-peixes-parana.streamlit.app/>

A publicação inicial usa a amostra redistribuível incluída no repositório e não
depende de um serviço PostgreSQL pago. Quando uma instância remota for
provisionada, basta configurar a credencial de leitura conforme as instruções
abaixo; o endereço público permanece o mesmo.

## Arquitetura de produção

O dashboard é publicado no Streamlit Community Cloud a partir de `main`, com
entrada em `app/app.py` e Python 3.12. O PostgreSQL deve ser uma instância remota
com TLS, backups automáticos e acesso restrito. A aplicação pública recebe
somente `DATABASE_URL`, usando o papel `biodiversity_app` de leitura.

`DATABASE_WRITE_URL` nunca deve ser configurada no dashboard público. Cargas e
atualizações do GBIF são executadas separadamente com o proprietário do schema.
Se o banco estiver temporariamente indisponível, a aplicação usa a amostra
redistribuível de `data/sample/` em modo somente leitura.

## Preparar o PostgreSQL

1. Crie uma instância PostgreSQL 17 com TLS e backups habilitados.
2. Restrinja a rede ao menor conjunto possível de origens e exija
   `sslmode=require` na URL externa.
3. Em um ambiente administrativo, configure `DATABASE_WRITE_URL` com o
   proprietário do schema e execute `python -m src.load`.
4. Crie o papel limitado usando `sql/create_dashboard_role.sql`:

```powershell
psql $env:DATABASE_WRITE_URL `
  -v app_role=biodiversity_app `
  -v app_schema=biodiversity `
  -f sql/create_dashboard_role.sql
```

5. Confirme privilégios e volume carregado:

```powershell
psql $env:DATABASE_WRITE_URL `
  -v app_role=biodiversity_app `
  -v app_schema=biodiversity `
  -f sql/production_checks.sql
```

6. Teste a URL limitada sem imprimir a credencial:

```powershell
$env:DATABASE_URL="postgresql://biodiversity_app:...@host:5432/biodiversidade_peixes?sslmode=require"
python -m src.query_db resumo
```

## Variáveis do Streamlit

No Streamlit Community Cloud, crie o aplicativo a partir de:

- repositório: `ThierryFabian00/biodiversidade-peixes`;
- branch: `main`;
- arquivo principal: `app/app.py`;
- Python: `3.12`.

Em **Advanced settings > Secrets**, copie as chaves de
`.streamlit/secrets.toml.example`, substituindo apenas a URL por uma credencial
real de leitura. Segredos de nível raiz ficam disponíveis como variáveis de
ambiente. Nunca envie `.env` ou `secrets.toml` ao GitHub.

## Verificação publicada

Depois do deploy:

1. abra a URL em uma janela anônima;
2. confirme que a fonte ativa é a amostra pública ou o PostgreSQL configurado;
3. alterne entre Brasil e Suíça;
4. teste mapa, série temporal, comparação, relatório e CSV;
5. confirme que a atualização GBIF está desabilitada;
6. repita em viewport de computador e celular;
7. confira
   `https://biodiversidade-peixes-parana.streamlit.app/~/+/_stcore/health`;
8. verifique os logs sem expor URLs de conexão.

## Recuperação

Se a conexão falhar, o dashboard exibe a amostra pública sem revelar detalhes
da credencial. Para reverter uma publicação, restaure a versão anterior no
Streamlit ou reverta o commit em `main`; não apague dados do PostgreSQL durante
o rollback da interface.
