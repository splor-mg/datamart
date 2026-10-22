# Laboratório PostgreSQL, Metabase e Giftless

Para a implantação atual com **templates do Easypanel**, siga o
[guia do banco PostgreSQL do Metabase](metabase-postgres-easypanel.md).
Os templates não executam os scripts dos Dockerfiles deste repositório.

O restante deste documento descreve a alternativa de **três App Services
independentes**, usando os Dockerfiles no branch `easypanel-labanca`, e o
Compose para desenvolvimento local. O projeto Django continua responsável
pelas migrations. O banco `datamart` recebe dados orçamentários; o banco
`metabase` guarda usuários, perguntas e painéis; Giftless guarda objetos
Git LFS em volume próprio. Consulte a
[pesquisa com fontes](easypanel-labanca-contexto.md) para o contexto dos issues.

## Alternativa: implantar no Easypanel com Dockerfiles

Crie os serviços `postgres`, `metabase` e `giftless` no mesmo projeto. Em
cada serviço, configure origem Git `https://github.com/splor-mg/datamart`,
branch **`easypanel-labanca`** e construção por Dockerfile. Em **Fonte >
Github**, o campo **Caminho de Build** define a pasta de contexto. Em
**Construção > Dockerfile**, o campo **Arquivo** é **`Dockerfile`** nos três
serviços, relativo à pasta escolhida:

| App Service | Caminho de Build | Arquivo | Ambiente de referência | Persistência | Porta |
|---|---|---|---|---|---|
| PostgreSQL | `/docker/postgres/` | `Dockerfile` | `docker/postgres/.env.example` | Volume em `/var/lib/postgresql/data` | TCP `5432` |
| Metabase | `/docker/metabase/` | `Dockerfile` | `docker/metabase/.env.example` | Dados no banco PostgreSQL `metabase` | HTTP `3000` |
| Giftless | `/docker/giftless/` | `Dockerfile` | `docker/giftless/.env.example` | Volume em `/lfs-storage` | HTTP `8080` |

Cada pasta é um contexto independente: os `COPY` usam arquivos da própria
pasta, sem repetir `docker/NOME_DO_SERVICO/`. O Metabase permanece em
`docker/metabase/Dockerfile`. Para construir diretamente pelo terminal:

```sh
docker build -t SEU_REGISTRY/datamart-postgres:labanca docker/postgres
docker build -t SEU_REGISTRY/datamart-metabase:labanca docker/metabase
docker build -t SEU_REGISTRY/datamart-giftless:labanca docker/giftless
```

Giftless publica imagem Linux amd64; use VM Azure x86_64. Cada pasta tem
sua `.dockerignore`, excluindo ambiente, certificados e cache Python.
Certificados e senhas entram em runtime, fora das imagens.
Scripts e configuração já estão nas imagens; não há bind mounts para
scripts no modelo App Service.

Cole no ambiente de **cada serviço** seu exemplo preenchido. Gere uma
senha/chave diferente para cada campo com:

```sh
python -c "import secrets; print(secrets.token_hex(32))"
```

Configure somente as variáveis de cada serviço. Metabase recebe sua senha
de banco e chave de criptografia; Giftless recebe suas duas chaves.
Preserve as chaves entre deploys. Os Dockerfiles trazem os comandos e
healthchecks; mantenha os overrides de comando/entrypoint do painel vazios.

### 1. PostgreSQL

Preencha `docker/postgres/.env.example` no ambiente. Adicione volume em
**`/var/lib/postgresql/data`**. Use uma réplica, com esse volume reservado
ao PostgreSQL; duas instâncias não podem escrever no mesmo diretório.

O servidor exige TLS e senha SCRAM nas conexões TCP. Configure dois mounts
de arquivo, em modo de leitura:

| Caminho no container | Conteúdo |
|---|---|
| `/certificates/server.crt` | Certificado PEM com cadeia intermediária |
| `/certificates/server.key` | Chave privada PEM sem passphrase |

Como alternativa, monte um diretório do host contendo esses arquivos em
`/certificates`. O certificado deve incluir o hostname externo nos SANs.
A chave é copiada para um diretório privado com as permissões exigidas
pelo PostgreSQL. Reinicie o serviço após renovar os arquivos.

O certificado automático do domínio web não configura TLS PostgreSQL.
Publique a porta **TCP** escolhida no host, com target `5432`. Na Azure,
libere-a no NSG e no firewall somente para IPs autorizados de desenvolvedores,
ETL e agentes. Aponte o DNS externo para a VM. VPN/túnel previamente
concedido também permite acesso sem conta no Easypanel.

Implante primeiro PostgreSQL e confira healthcheck/logs. A imagem cria os
bancos `datamart` e `metabase`, roles e schemas `dados_siafi`/`linktable`
somente com volume vazio. Alterar senhas no ambiente depois requer alterar
também as roles com `ALTER ROLE` e atualizar clientes. Preserve o volume.

### 2. Metabase

Preencha `docker/metabase/.env.example`:

- `MB_DB_HOST`: DNS interno PostgreSQL. Templates oficiais do Easypanel
  usam `NOME_DO_PROJETO_NOME_DO_SERVICO`, por exemplo `datamart-labanca_postgres`.
  Confirme no painel o endereço e a rede compartilhada. O nome curto
  `postgres` do Compose local não é uma garantia entre App Services.
- `MB_DB_PASS`: **mesmo valor de `METABASE_DB_PASSWORD`** no PostgreSQL.
- `MB_ENCRYPTION_SECRET_KEY`: chave própria e persistente para proteger
  credenciais das fontes de dados.
- `MB_SITE_URL`: domínio HTTPS público Metabase.

A imagem monta URI JDBC com `sslmode=require` usando host/porta/banco e
preserva a inicialização oficial. Pode-se fornecer `MB_DB_CONNECTION_URI`
para outra política de certificado; coloque a senha somente em `MB_DB_PASS`.
O Metabase usa PostgreSQL, não o H2 embutido.

Associe o domínio, por exemplo `bi-lab.exemplo.gov.br`, ao proxy HTTP na
porta interna **3000**, com HTTPS. Implante após PostgreSQL saudável.
Não existe `depends_on` entre App Services; o painel gerencia os deploys
separadamente. Se o banco estiver indisponível, corrija a conexão e
reimplante Metabase.

Abra a interface, crie o administrador inicial e cadastre a fonte analítica:

| Campo | Valor |
|---|---|
| Host | Mesmo DNS interno usado em `MB_DB_HOST` |
| Porta | `5432` |
| Banco | `datamart` |
| Usuário | `metabase_reader` |
| Senha | `METABASE_READER_PASSWORD` do PostgreSQL |
| SSL | Ativado |

O banco interno `metabase` guarda a configuração da aplicação e não deve
ser fonte analítica. O leitor recebe `SELECT` nas tabelas criadas por
`datamart` em `public`, `dados_siafi` e `linktable`, inclusive novas tabelas.
Outras roles/schemas precisam de grants próprios.

Para o issue Projetos #24, teste grupos/coleções por área com contas comuns
e restrinja primeiro `All Users`. As permissões mais amplas prevalecem.
Na Community, administradores são globais; administração independente
por organização não vem pronta.

### 3. Giftless

Preencha `docker/giftless/.env.example` e adicione volume em **`/lfs-storage`**.
A imagem preserva o usuário `giftless` e o dono desse diretório. Se o painel
usar um diretório de host novo, assegure que o usuário possa escrever nele.

O script injeta as chaves JWT em runtime e inicia `tini`/uWSGI HTTP na porta
**8080**. Associe domínio próprio, por exemplo `lfs-lab.exemplo.gov.br`, ao
proxy nessa porta, com HTTPS. Giftless é independente dos demais serviços.

O proxy deve preservar `Authorization` e sobrescrever `X-Forwarded-Proto`,
`X-Forwarded-Host` e `X-Forwarded-Port`; a configuração confia em um proxy.
Use domínio sem prefixo de caminho e confirme que os `href` batch apontam
para o domínio HTTPS público. Ajuste limites de tamanho/timeout para os
arquivos esperados. Logs de requisições uWSGI estão desativados porque URLs
podem conter tokens; o proxy também deve ocultar esses parâmetros nos logs.

Na console do App Service, o operador emite um token:

```sh
python /app/create-token.py --subject desenvolvedor --scope 'obj:splor-mg/REPO/*:read,write,verify' --hours 8
```

Para leitura, use `--scope 'obj:splor-mg/REPO/*:read'`. Tokens têm validade
e precisam ser renovados. Entregue tokens ao desenvolvedor, preservando
as chaves de assinatura com o operador. A chave do cliente e a chave das
autorizações temporárias são diferentes; estas últimas duram 15 minutos.

No repositório de dados do desenvolvedor:

```sh
git lfs install
git config --local lfs.url https://lfs-lab.exemplo.gov.br/splor-mg/REPO.git/info/lfs
git config --local lfs.locksverify false
git lfs track '*.csv.gz'
```

Use usuário **`_jwt`** e JWT como senha com um credential helper. Agentes
HTTP usam `Authorization: Bearer TOKEN` e `POST .../objects/batch` do Git LFS.
`REPO` deve coincidir na URL e no scope; Giftless não verifica sua existência
no GitHub. Tokens ficam fora do Git, da URL configurada e das instruções
versionadas do agente.

O servidor Git guarda commits/ponteiros; Giftless guarda objetos grandes.
Isso não converte arquivos atuais nem altera o upload da API GitHub usado
pelo ETL. O produtor precisa usar um cliente Git LFS.

## Acesso de desenvolvedores e agentes

Usuários não precisam de conta no Easypanel. Entregue por canal privado
credenciais e endpoints autorizados:

| Serviço | Endpoint de exemplo | Interface e credencial |
|---|---|---|
| PostgreSQL | `pg-lab.exemplo.gov.br:5432` | SQL/TCP com TLS, usuário/senha; sem interface web |
| Metabase | `https://bi-lab.exemplo.gov.br` | Navegador/API, conta individual/API key |
| Giftless | `https://lfs-lab.exemplo.gov.br/splor-mg/REPO.git/info/lfs` | Git LFS/API HTTP, JWT; sem painel web |

No SQL, `datamart` é proprietário do seu banco e executa migrations/ETL;
`metabase_reader` permite leitura. Para contas individuais, crie roles
`LOGIN` associadas à role apropriada. Use `SET ROLE datamart` ao criar
tabelas para manter grants automáticos do leitor. A senha do superusuário
PostgreSQL fica somente com o operador.

Clientes externos devem verificar CA/hostname com `sslmode=verify-full`.
Para CA privada, forneça seu certificado, por exemplo:

```sh
psql "host=pg-lab.exemplo.gov.br port=5432 dbname=datamart user=datamart sslmode=verify-full sslrootcert=/caminho/ca.crt" -W
```

`sslmode=require` cifra, mas não verifica CA/hostname; é a opção interna
padrão Metabase na rede do projeto. DBeaver/drivers Python também permitem
validação TLS. O ETL usa `PG_URL` com senha codificada se tiver caracteres
reservados: `postgresql://datamart:SENHA@HOST:5432/datamart?sslmode=verify-full`.

No Metabase, use conta individual com grupos apropriados. Agentes usam a
[API oficial](https://www.metabase.com/docs/latest/api-documentation) com
`X-API-Key`. O operador cria chaves associadas ao grupo em
**Admin > Settings > Authentication > API keys**; `/api/docs` descreve a API.

## Desenvolvimento local

`compose.yaml` mantém os containers juntos para uso local. O complemento
`compose.external.yaml` adiciona TLS local. Estes não são a implantação
dos três App Services no Easypanel.

```sh
cp .env.compose.example .env.compose
# Preencha as senhas/chaves diferentes antes de executar:
docker compose --env-file .env.compose config --quiet
docker compose --env-file .env.compose up -d --wait --wait-timeout 600
```

No PowerShell, use `Copy-Item`. Endereços locais: Metabase `localhost:3000`,
Giftless `localhost:8080`, SQL `localhost:5432`. Para TLS local, coloque
certificados em `.certs/postgres/` e use `-f compose.yaml -f compose.external.yaml`.
Exemplos `.env` por Dockerfile são para App Services; `.env.compose.example`
é para o Compose.

Django continua com Poetry. Configure seu `.env` com `DB_NAME=datamart`,
`DB_USER=datamart`, senha `DATAMART_PASSWORD` e host/porta do banco. Execute
`poetry run task migrate`. A carga SIAFI/Linktable depende do ETL e não é
executada automaticamente pelas imagens.

## Operação e verificação

Verifique healthchecks/logs em cada App Service. Giftless responde `404`
na raiz por não ter página web; Metabase oferece `/api/health`. Confirme
leitura/bloqueio de escrita SQL, TLS externo, transferências e persistência.

Faça backup de **ambos** os bancos PostgreSQL e do volume Giftless. Para
migrar um Compose já implantado para App Services, faça backup/restore e
mova os objetos LFS: os volumes do painel são outros. Trocar implantação
não transfere dados automaticamente. Preserve também as chaves desse ambiente.

Os Dockerfiles foram construídos e executados como containers independentes
em 22/10/2026, com rede, portas, ambientes e volumes isolados. A validação
incluiu healthchecks, inicialização SQL, conexão TLS interna Metabase,
TLS externo, permissões SQL, JWT e transferência/persistência Giftless.
Domínios, certificados reais e NSG precisam ser configurados na VM Azure.

O build também foi verificado em 22/10/2026 usando a pasta de cada serviço
como contexto, conforme o **Caminho de Build** do painel. Esse formato
evita a falha de `COPY ... not found` quando o Easypanel constrói a imagem
a partir de `/docker/postgres/`, `/docker/metabase/` ou `/docker/giftless/`.
