# Metabase dos templates Easypanel: banco interno PostgreSQL

Pesquisa em 22/10/2026. O usuário informou que os serviços foram implantados
pelos templates nativos do Easypanel e que o Metabase exibiu o aviso sobre
H2. As conclusões abaixo vêm de fontes oficiais; não houve acesso à VM,
consulta às credenciais do painel ou migração da instalação em execução.

## Por que o template usa H2

O [gerador oficial do template Metabase](https://github.com/easypanel-io/templates/blob/main/templates/metabase/index.ts)
cria somente um App Service, define `MB_DB_FILE=/metabase-data/metabase.db`
e monta o volume `data` em `/metabase-data`. Ele não configura `MB_DB_TYPE`
nem cria um banco PostgreSQL. A
[referência oficial de variáveis Metabase](https://www.metabase.com/docs/latest/configuring-metabase/environment-variables#mb_db_type)
define H2 como o padrão de `MB_DB_TYPE`; esse conjunto explica o aviso.

O [arquivo de metadados do template](https://github.com/easypanel-io/templates/blob/main/templates/metabase/meta.yaml)
consultado oferece `metabase/metabase:v0.60.3.6` como imagem padrão. Isso não
confirma a versão implantada na VM. O operador deve conferir a imagem/tag
efetiva antes de migrar e fixar essa mesma versão durante a operação.

O [banco interno do Metabase](https://www.metabase.com/docs/latest/installation-and-operation/configuring-application-database)
guarda contas, perguntas, painéis e outras configurações. Ele é distinto da
fonte analítica, como o banco `datamart`, que se cadastra pela interface web.
Cadastrar uma fonte PostgreSQL em **Admin > Databases** não muda o H2 interno.

## Reutilizar o PostgreSQL existente

A documentação Metabase recomenda PostgreSQL para o banco interno e
permite configurar a conexão com `MB_DB_TYPE=postgres`, `MB_DB_HOST`,
`MB_DB_PORT`, `MB_DB_DBNAME`, `MB_DB_USER` e `MB_DB_PASS`. A configuração é
lida ao iniciar: requer salvar o ambiente e reimplantar o App Service.
Metabase cria suas tabelas e executa migrations, mas
[não cria o banco PostgreSQL](https://www.metabase.com/docs/latest/installation-and-operation/configuring-application-database#postgresql).
Crie previamente um banco UTF-8 vazio e uma role exclusiva proprietária.
Isso pode ocorrer no servidor PostgreSQL que já existe; não há requisito
de um novo container ou de um Compose para o banco interno.

O [template oficial Directus](https://github.com/easypanel-io/templates/blob/main/templates/directus/index.ts)
usa `DB_HOST=$(PROJECT_NAME)_NOME_DO_SERVICO`, porta `5432` e usuário
administrativo `postgres` para seu serviço Postgres nativo. Esse é o
padrão de DNS interno a conferir nas credenciais/rede do painel. Para
projeto `datamart` e serviço `datamart-postgres`, o endereço esperado é
`datamart_datamart-postgres`; não foi validado na VM. `localhost` dentro
do Metabase aponta para o próprio container, não para PostgreSQL.

Metabase usa o schema `public` para seu banco interno, conforme
[MB_DB_CONNECTION_URI](https://www.metabase.com/docs/latest/configuring-metabase/environment-variables#mb_db_connection_uri).
No [catálogo PostgreSQL 17](https://github.com/postgres/postgres/blob/REL_17_STABLE/src/include/catalog/pg_namespace.dat),
o proprietário inicial de `public` é `pg_database_owner`. Em bancos novos,
o dono do banco pode criar suas tabelas; um grant explícito de `USAGE` e
`CREATE` em `public` à role Metabase também cobre configurações ajustadas.
Metabase precisa desses direitos para executar suas migrations, sem
necessidade de usar uma conta superusuária na aplicação.

## TLS e ambiente

O [serviço Postgres nativo](https://easypanel.io/docs/services/postgres)
se baseia na imagem oficial PostgreSQL. Sua documentação descreve
publicação por porta para acesso remoto. O
[proxy de App Services](https://easypanel.io/docs/services/app#domains--proxy)
configura certificados Let's Encrypt para domínios HTTPS de aplicações.
Isso não declara configuração TLS no protocolo PostgreSQL nem montagem
automática de certificado no container do banco.

Para a conexão interna ao template nativo, as seis variáveis acima são a
configuração inicial recomendada. Não reaproveite a URI `sslmode=require`
do Dockerfile customizado sem confirmar que o servidor aceita TLS.
`MB_DB_CONNECTION_URI` é opcional e prevalece sobre os campos separados,
conforme o [código de configuração Metabase](https://github.com/metabase/metabase/blob/master/src/metabase/app_db/env.clj).
Uma URI antiga de H2 ou com política TLS incompatível pode impedir a troca.
TLS explícito, quando provisionado no servidor, é configurável pela URI JDBC.
Não há variável booleana `MB_DB_SSL` na referência do banco interno.

`MB_ENCRYPTION_SECRET_KEY` é opcional na imagem oficial e serve para
[cifrar credenciais das fontes](https://www.metabase.com/docs/latest/databases/encrypting-details-at-rest).
Em uma instalação nova, gere uma chave aleatória, por exemplo com
`openssl rand -base64 32`, e preserve-a entre deploys. Se a instalação
existente já tem essa chave, use o mesmo valor durante e após a migração.
Adicionar ou trocar criptografia é uma operação separada: não misture
rotação de chave com a troca do banco interno.

## Base nova ou migração H2

Se não há conteúdo a preservar, apontar as variáveis para um PostgreSQL
vazio inicia uma instalação nova. Isso não importa usuários, perguntas
ou painéis existentes no H2. Guarde o volume H2 antes de alterar o ambiente.

Se há conteúdo a preservar, a
[migração oficial de H2](https://www.metabase.com/docs/latest/installation-and-operation/migrating-from-h2)
é uma operação única com `load-from-h2`. Seus requisitos são:

- usar a mesma versão de Metabase que gravou o H2, na migração e no primeiro
  início com PostgreSQL; realizar upgrades depois de validar a migração;
- parar a instância para não haver escrita concorrente e fazer backup do H2;
- testar conectividade com o destino a partir do ambiente de migração;
- usar um banco PostgreSQL novo e vazio; não iniciar o Metabase normal nele
  antes da importação;
- executar a migração em uma cópia do H2, preservar a original e a chave
  de criptografia existente, quando houver;
- passar o caminho base sem o sufixo `.mv.db` ou `.h2.db`;
- iniciar o Metabase normalmente apenas depois de `load-from-h2` terminar
  com sucesso, com as variáveis de PostgreSQL e sem o comando de importação.

O caminho real precisa ser localizado no volume. O
[entrypoint oficial v0.60.3.6](https://github.com/metabase/metabase/blob/v0.60.3.6/bin/docker/run_metabase.sh)
pode reorganizar o H2 ao reduzir privilégios: o arquivo pode ficar em
`/metabase-data/metabase.db/metabase.db.mv.db`, além do caminho mais simples
`/metabase-data/metabase.db.mv.db`. Confira com:

```sh
find /metabase-data -type f \( -name '*.mv.db' -o -name '*.h2.db' \)
```

O mesmo entrypoint confirma `/app/metabase.jar` como o JAR da imagem. Em
um container temporário de migração com a mesma imagem, a cópia H2 montada
e as variáveis do PostgreSQL, o comando Java é:

```sh
java --add-opens java.base/java.nio=ALL-UNNAMED -jar /app/metabase.jar \
  load-from-h2 /copia/metabase.db
```

Nesse exemplo, o arquivo montado deve ser `/copia/metabase.db.mv.db`, e
`/copia` precisa permitir escrita para os arquivos auxiliares de H2. Não
execute esse comando na console de uma instância que continua servindo
usuários. Alternativamente, o guia oficial Docker permite copiar o H2
para outro ambiente, baixar o JAR da mesma versão e executar o comando
fora do container, desde que exista conexão autorizada ao PostgreSQL.

O [guia oficial](https://www.metabase.com/docs/latest/installation-and-operation/migrating-from-h2#how-can-i-tell-if-my-metabase-instance-uses-h2)
indica `GET /api/bug-reporting/details` para verificar como administrador
se `application-database` passou a `postgres`. Depois, confirme login,
perguntas e painéis e faça backup do banco PostgreSQL; mantenha o backup H2.
