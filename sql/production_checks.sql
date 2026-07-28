\set ON_ERROR_STOP on

\if :{?app_role}
\else
\set app_role biodiversity_app
\endif

\if :{?app_schema}
\else
\set app_schema biodiversity
\endif

SELECT rolname,
       NOT rolsuper AS sem_superusuario,
       NOT rolcreatedb AS sem_criar_banco,
       NOT rolcreaterole AS sem_criar_papel
FROM pg_roles
WHERE rolname = :'app_role';

SELECT has_database_privilege(:'app_role', current_database(), 'CONNECT')
       AS pode_conectar,
       has_schema_privilege(:'app_role', :'app_schema', 'USAGE')
       AS pode_usar_schema,
       NOT has_schema_privilege(:'app_role', :'app_schema', 'CREATE')
       AS nao_pode_criar_no_schema;

SELECT format(
    'SELECT %L AS tabela, has_table_privilege(%L, %L, ''SELECT'') AS pode_ler, '
    'NOT has_table_privilege(%L, %L, ''INSERT,UPDATE,DELETE,TRUNCATE'') AS sem_escrita',
    :'app_schema' || '.occurrences',
    :'app_role',
    :'app_schema' || '.occurrences',
    :'app_role',
    :'app_schema' || '.occurrences'
)
\gexec

SELECT format(
    'SELECT country_code, COUNT(*) AS ocorrencias FROM %I.occurrences '
    'GROUP BY country_code ORDER BY country_code',
    :'app_schema'
)
\gexec
