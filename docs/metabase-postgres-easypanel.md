# Metabase com PostgreSQL usando os templates do Easypanel

O aviso `Using Metabase with an H2 application database` informa que o
Metabase guarda usuários, perguntas, dashboards e configurações em um
arquivo H2. O serviço pode iniciar assim, mas o Metabase recomenda
PostgreSQL para o banco da aplicação em produção.

A implantação escolhida usa os templates do Easypanel. É possível
reutilizar o PostgreSQL que já está rodando: basta criar nele um banco e
uma role exclusivos para o Metabase. Não é necessário outro container
PostgreSQL nem um novo Compose. Esse banco é separado dos dados
orçamentários que serão cadastrados como fonte analítica na interface.

As variáveis abaixo são para o **template / imagem oficial**. O
`docker/metabase/Dockerfile` deste repositório é uma alternativa com
inicialização e TLS próprios; não é necessário usá-lo com os templates.
Veja também a [pesquisa com fontes oficiais](metabase-postgres-contexto.md).

## 1. Instalação nova

Como esta instância acabou de ser instalada e não há conteúdo a preservar,
o procedimento escolhido é criar o banco PostgreSQL vazio e alterar o
ambiente do Metabase. Não é necessário migrar o H2. O Metabase apresentará
o assistente inicial para configurar a nova instalação.

Se já existem usuários, perguntas, dashboards ou fontes cadastradas que
devem ser preservados, consulte a seção 4 antes de iniciar o
Metabase com as novas variáveis. Trocar `MB_DB_TYPE` **não importa o H2**.
Mesmo na instalação nova, preserve o volume H2 até validar o resultado.

## 2. Criar o banco no PostgreSQL existente

No serviço PostgreSQL, consulte **Credenciais** e anote o hostname
interno, usuário administrador e porta interna. Use a rede do projeto e
porta `5432`; não é necessário publicar uma porta na Azure para essa
comunicação. O nome ilustrativo `datamart_datamart-postgres` deve ser
substituído pelo endereço realmente exibido no painel.

Abra o console do PostgreSQL e execute `psql` com o administrador indicado
nas credenciais, conectado ao banco `postgres`:

```sh
psql -U USUARIO_ADMIN -d postgres
```

Se necessário, acrescente `-h 127.0.0.1 -W` para solicitar sua senha.
Antes de criar, liste as roles e bases com `\du` e `\l`. Se `metabase` já
existir, confira proprietário, permissões e conteúdo; não execute o
script novamente nem apague dados para contornar o erro.

No `psql`, envie primeiro:

```sql
\set ON_ERROR_STOP on
CREATE ROLE metabase LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE;
\password metabase
```

Digite a nova senha duas vezes quando solicitada; guarde esse valor para
`MB_DB_PASS`. Só depois do prompt de senha envie o restante:

```sql
CREATE DATABASE metabase OWNER metabase ENCODING 'UTF8' TEMPLATE template0;
REVOKE ALL ON DATABASE metabase FROM PUBLIC;
\connect metabase
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE, CREATE ON SCHEMA public TO metabase;
\q
```

O procedimento cria uma role sem poderes administrativos e um banco que
ela pode modificar para manter o Metabase. Os mesmos comandos estão no
arquivo [create-application-database.sql](../docker/metabase/create-application-database.sql),
que também pode ser executado com `psql -f` se for disponibilizado no
container. Ele não é copiado automaticamente pelo template.

Esse procedimento é executado no banco já existente. Os scripts de
`docker-entrypoint-initdb.d` dos Dockerfiles deste repositório **não são
executados pelos templates**, e adicionar variáveis ao PostgreSQL já
inicializado não cria outra role ou banco.

## 3. Configurar o ambiente do template Metabase

Em **Metabase > Ambiente**, mantenha os ajustes necessários do template e
adicione o exemplo
[`.env.easypanel-template.example`](../docker/metabase/.env.easypanel-template.example)
preenchido:

```dotenv
MB_DB_TYPE=postgres
MB_DB_HOST=HOSTNAME_INTERNO_DO_POSTGRES
MB_DB_PORT=5432
MB_DB_DBNAME=metabase
MB_DB_USER=metabase
MB_DB_PASS=SENHA_DA_ROLE_METABASE
MB_SITE_URL=https://DOMINIO_DO_METABASE
```

Substitua os placeholders. A senha aqui é a da role `metabase` criada no
passo anterior, e não a senha do administrador PostgreSQL. Remova
`MB_DB_FILE`, se presente, e uma eventual `MB_DB_CONNECTION_URI` antiga:
uma URI explícita pode sobrescrever host, porta e nome do banco.

O template nativo do PostgreSQL e o Dockerfile com TLS são configurações
diferentes. As variáveis acima usam a rede interna, sem impor
`sslmode=require` do wrapper personalizado. O Let’s Encrypt do Easypanel
continua cuidando do **HTTPS da interface Metabase**; ele não monta um
certificado dentro do PostgreSQL. Para clientes externos ao servidor,
use túnel/VPN ou configure TLS do PostgreSQL separadamente.

`MB_ENCRYPTION_SECRET_KEY` é opcional na imagem oficial. Se já estava
configurada, preserve exatamente a mesma chave no processo de migração e
nos deploys seguintes. Para uma instância nova, pode-se gerar uma chave
com `openssl rand -base64 32`. Senhas,
chaves e backups ficam fora do Git.

Com PostgreSQL disponível e a base pronta, salve e reimplante o Metabase.
Não altere domínio/porta do proxy: a interface continua na porta HTTP
interna `3000` e no domínio HTTPS existente.

## 4. Se houver conteúdo a preservar

Esta etapa não é necessária para a instalação nova. Se descobrir conteúdo
importante no H2, pare o serviço e faça backup antes de alterar a conexão.
Siga a [migração oficial](https://www.metabase.com/docs/latest/installation-and-operation/migrating-from-h2)
com `load-from-h2`, a mesma versão Metabase, a chave de criptografia
existente e um banco PostgreSQL vazio. O
[registro da pesquisa](metabase-postgres-contexto.md#base-nova-ou-migração-h2)
reúne os requisitos e como localizar o arquivo do template.

## 5. Verificar e operar

Verifique os logs: o aviso de uso do H2 deve desaparecer e a inicialização
deve concluir com conexão ao PostgreSQL. Consulte `/api/health` e abra a
interface. Em uma instalação nova, aparecerá o assistente inicial; após
migração, deverão existir os usuários e conteúdos anteriores.

No console PostgreSQL, confira que há tabelas da aplicação:

```sh
psql -U USUARIO_ADMIN -d metabase -c '\dt public.*'
```

Faça backups do banco `metabase`, além do banco analítico. O volume H2
não passa a ser um backup automático do PostgreSQL. Cadastrar uma fonte
em **Admin > Bancos de dados** é uma operação separada e não muda o banco
interno usado para guardar a configuração da aplicação.

Em 22/10/2026, o script foi validado em containers locais isolados com
`postgres:17.11-alpine` e `metabase/metabase:v0.64.1`, usando as seis
variáveis de conexão. A role autenticou, o Metabase criou suas tabelas,
`/api/health` respondeu com sucesso e o aviso H2 não apareceu. Os recursos
temporários foram removidos. A versão do template na VM deve ser conferida
no painel; não houve acesso à Azure nem migração da instância em execução.
