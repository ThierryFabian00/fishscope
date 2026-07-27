\set ON_ERROR_STOP on

\if :{?app_role}
\else
\set app_role biodiversity_app
\endif

\if :{?app_schema}
\else
\set app_schema biodiversity
\endif

\if :{?app_password}
\else
\prompt 'Senha do usuário de leitura do dashboard: ' app_password
\endif

SELECT format(
    'CREATE ROLE %I LOGIN PASSWORD %L NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT',
    :'app_role', :'app_password'
)
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'app_role')
\gexec

SELECT format(
    'ALTER ROLE %I WITH LOGIN PASSWORD %L NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT',
    :'app_role', :'app_password'
)
\gexec

SELECT format('GRANT CONNECT ON DATABASE %I TO %I', current_database(), :'app_role')
\gexec
SELECT format('GRANT USAGE ON SCHEMA %I TO %I', :'app_schema', :'app_role')
\gexec
SELECT format('GRANT SELECT ON ALL TABLES IN SCHEMA %I TO %I', :'app_schema', :'app_role')
\gexec
SELECT format(
    'ALTER DEFAULT PRIVILEGES IN SCHEMA %I GRANT SELECT ON TABLES TO %I',
    :'app_schema', :'app_role'
)
\gexec
SELECT format('REVOKE CREATE ON SCHEMA public FROM %I', :'app_role')
\gexec
