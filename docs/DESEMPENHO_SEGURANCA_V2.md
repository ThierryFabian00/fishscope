# Desempenho e segurança

## Limites operacionais

- A busca GBIF aceita páginas de até 300 registros e amostras interativas de
  5.000 registros.
- A consulta do dashboard carrega no máximo 50.000 registros por país, valor
  configurável por `LIMITE_REGISTROS_DASHBOARD` e nunca superior ao teto técnico
  de 100.000 da busca.
- Consultas analíticas de ranking ou espécie retornam no máximo 1.000 linhas; o
  termo científico aceita até 200 caracteres.
- A tabela e o seletor de detalhes enviam no máximo 1.000 registros ao
  navegador; o download CSV mantém todo o recorte já limitado da consulta.
- Acima de 5.000 pontos válidos, o mapa agrega as ocorrências em uma grade de no
  máximo 5.000 células antes de enviar dados ao navegador. As contagens das
  células preservam o total de ocorrências.

Quando o PostgreSQL possui mais linhas que o teto do dashboard, a interface
informa quantos registros foram carregados e quantos estavam disponíveis.

## Cache e conexões

Dados por país permanecem em cache por cinco minutos, com no máximo 12 entradas.
Relatórios PDF usam cache separado com até 20 entradas, e o limite geográfico
possui duas entradas. Uma carga de país consulta ocorrências e resumo da última
importação usando a mesma conexão PostgreSQL.

O dashboard não consulta mais o status de sincronização em toda abertura. O
GBIF e a conexão de escrita são acessados somente quando o usuário solicita uma
atualização.

## Credenciais separadas

Use duas URLs:

- `DATABASE_URL`: usuário `biodiversity_app`, somente leitura, usado pelo
  dashboard;
- `DATABASE_WRITE_URL`: proprietário do schema, usado apenas na atualização
  explícita e nos comandos de carga.

Depois de criar o schema com o proprietário, crie ou atualize o papel de leitura:

```powershell
docker compose exec db psql `
  -U biodiversity_owner `
  -d biodiversidade_peixes `
  -v app_role=biodiversity_app `
  -v app_schema=biodiversity `
  -f /opt/biodiversity/sql/create_dashboard_role.sql
```

O script solicita a senha interativamente e concede apenas `CONNECT`, `USAGE` e
`SELECT`. O papel recebe `NOSUPERUSER`, `NOCREATEDB`, `NOCREATEROLE` e não pode
criar objetos no schema `public`.

## Proteção de segredos

O arquivo `.env` permanece ignorado pelo Git. Mensagens exibidas e logs passam
por uma camada que mascara senhas em URLs e campos chamados `password`,
`passwd`, `pwd`, `secret` ou `token`. Erros do PostgreSQL são apresentados de
forma controlada sem incluir a senha da conexão.

Não coloque URLs reais em código, documentação, prints, issues ou commits. Use
os valores fictícios de `.env.example` apenas como modelo e escolha senhas
próprias para cada ambiente.

## Falhas controladas

Timeout, indisponibilidade ou erro HTTP do GBIF, ausência de dados, período
inválido, limite excessivo e falhas PostgreSQL produzem mensagens curtas e
acionáveis. Uma atualização que falha não remove o snapshot anterior do banco.
