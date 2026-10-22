# Contexto do laboratório PostgreSQL, Metabase e Giftless

Pesquisa realizada em 21/10/2026, a partir dos issues completos, incluindo
comentários, e da documentação e implementação oficiais dos serviços.

## Necessidades identificadas

- O [issue Datamart #26](https://github.com/splor-mg/datamart/issues/26)
  acompanha a construção da Linktable e sua integração ao ETL. No
  [comentário de 05/10/2026](https://github.com/splor-mg/datamart/issues/26#issuecomment-5996515573),
  um arquivo `linktable.csv.gz` de 92,1 MB excedeu o tamanho aceito pela API
  GitHub. A proposta registrada é carregar as tabelas diretamente no
  PostgreSQL, usando `PG_URL`, schema `linktable`, `COPY` e uma única
  transação; publicar no GitHub apenas o descriptor para manter histórico.
  A configuração da conexão não deve incluir senha no descriptor.
- O [issue Projetos #24](https://github.com/splor-mg/projetos/issues/24)
  trata da substituição dos painéis e dos níveis de acesso. Nos
  [comentários de 21/10/2026](https://github.com/splor-mg/projetos/issues/24#issuecomment-6317664618),
  a orientação é criar uma instância de teste de PostgreSQL com dados
  SIAFI, conectar o Metabase e explorar os níveis de acesso.
- O [issue Datamart #19](https://github.com/splor-mg/datamart/issues/19)
  registra a necessidade de definir quem pode acessar o banco e quais IPs
  são permitidos. O
  [tutorial do Handbook citado no issue #24](https://splor-mg.github.io/handbook/blog/banco-de-dados-do-projeto-datamart/#postgresql)
  descreve Django para migrations, PostgreSQL para desenvolvimento e
  produção e restrição da porta externa a IPs confiáveis.

O Compose fornece a infraestrutura do laboratório. Construção da Linktable,
implementação de `dpetl[postgres]`, importação dos dados SIAFI e configuração
dos usuários e painéis dependem dos fluxos descritos nesses projetos e
continuam sendo etapas próprias.

## PostgreSQL e Metabase

O [README atual do Datamart](../README.pt-BR.md) define PostgreSQL como banco
central e Django como responsável pela estrutura e migrations. Isso permite
que a aplicação existente use o banco do laboratório sem acrescentar um
quarto container ao escopo solicitado.

O Metabase usa dois tipos de conexão distintos:

1. **Banco da aplicação:** guarda usuários, grupos, perguntas, coleções,
   dashboards e configuração do próprio Metabase. A documentação recomenda
   PostgreSQL para persistir esses dados, em vez do H2 embutido. A conexão
   é configurada por `MB_DB_TYPE`, `MB_DB_HOST`, `MB_DB_PORT`, `MB_DB_DBNAME`,
   `MB_DB_USER` e `MB_DB_PASS`.
2. **Fonte analítica:** banco `datamart`, adicionado pela interface de
   configuração do Metabase. É recomendável usar um usuário de leitura,
   separado do proprietário que executa migrations e ETL.

Fonte: [Metabase no Docker](https://www.metabase.com/docs/latest/installation-and-operation/running-metabase-on-docker).
A imagem oficial publica HTTP na porta `3000`, inclui `curl` e documenta
`/api/health` como endpoint de verificação. O release oficial estável
encontrado foi
[v0.64.1, publicado em 07/10/2026](https://github.com/metabase/metabase/releases/tag/v0.64.1).

A [imagem oficial PostgreSQL](https://github.com/docker-library/docs/blob/master/postgres/README.md)
executa scripts de `/docker-entrypoint-initdb.d` somente na inicialização de
um diretório de dados vazio. Assim, banco, roles e grants iniciais podem ser
preparados por um script, mas alterar variáveis de senha depois não altera
as senhas já armazenadas. Para PostgreSQL 17 e anteriores, o volume deve ser
montado em `/var/lib/postgresql/data`; a imagem 18 mudou esse layout.

### Limites de permissões do Metabase Community

O Metabase permite criar grupos e controlar acesso a bancos, schemas,
tabelas e coleções de perguntas e dashboards. Todos os usuários pertencem
também ao grupo `All Users`; as permissões mais amplas prevalecem entre os
grupos, portanto esse grupo precisa ter uma configuração restrita durante
o teste. Administradores globais têm acesso irrestrito aos dados.

O recurso **Group managers** é oferecido nos planos pagos. Mesmo nesse
recurso, o gestor não pode criar grupos nem convidar pessoas novas para a
instância. Assim, uma instância Community serve para avaliar grupos,
leitura e edição de coleções, mas não comprova automaticamente a exigência
original de um administrador independente por organização.

Fontes: [People and groups](https://www.metabase.com/docs/latest/people-and-groups/managing)
e [Permissions overview](https://www.metabase.com/docs/latest/permissions/start).

## Giftless

Giftless implementa o protocolo de servidor **Git LFS**, com adaptadores de
armazenamento local, Google Cloud Storage, Azure Blob Storage e Amazon S3.
O servidor Git continua guardando commits e pequenos ponteiros LFS; o
Giftless armazena os objetos grandes. Instalar Giftless não muda sozinho o
fluxo de publicação de arquivos via API GitHub descrito no issue #26:
o produtor precisa usar um cliente Git LFS e configurar seu endpoint.

Fontes: [README oficial](https://github.com/datopian/giftless)
e [Quickstart](https://giftless.datopian.com/en/latest/quickstart.html).

### Imagem, HTTP e persistência

- O release mais recente encontrado foi
  [v0.6.2](https://github.com/datopian/giftless/releases/tag/v0.6.2), publicado
  em 16/12/2024. O
  [workflow oficial](https://github.com/datopian/giftless/blob/v0.6.2/.github/workflows/ci.yaml)
  publica imagens no GitHub Container Registry.
- A consulta ao registry com `docker manifest inspect` confirmou
  `ghcr.io/datopian/giftless:v0.6.2` para **Linux amd64**. A tag sem o `v`,
  `ghcr.io/datopian/giftless:0.6.2`, retornou `manifest unknown`. O manifesto
  amd64 consultado tem digest
  `sha256:713f716d8f27a6debf91a97857c6958eabad51c9ae6490e278f816437c4a3ff7`.
- O [Dockerfile da release](https://github.com/datopian/giftless/blob/v0.6.2/Dockerfile)
  inicia `tini -- uwsgi`, com socket uWSGI em `127.0.0.1:5000` como padrão.
  É necessário sobrescrever os argumentos para servir **HTTP** em
  `0.0.0.0:8080`, preservando o entrypoint. Os argumentos documentados são
  `-M -T --threads 2 -p 2 --manage-script-name --callable app --http 0.0.0.0:8080`.
- O mesmo Dockerfile cria `/lfs-storage`, atribui esse diretório ao usuário
  `giftless` e configura o backend local. Um volume nomeado nesse caminho
  mantém os objetos entre recriações dos containers.

Fonte adicional: [Installation / Deployment](https://giftless.datopian.com/en/latest/installation.html).
A documentação ainda menciona Docker Hub; a publicação no GHCR foi
confirmada também no código e no registry, evitando depender dessa indicação
antiga.

### Configuração e autenticação

O Giftless aceita um arquivo YAML por `GIFTLESS_CONFIG_FILE` ou uma string
YAML/JSON por `GIFTLESS_CONFIG_STR`. O
[código da release](https://github.com/datopian/giftless/blob/v0.6.2/giftless/config.py)
usa prefixo `GIFTLESS_` para sobrescrever opções por variável de ambiente.
Esse detalhe difere de alguns exemplos antigos da documentação que
incluem `GIFTLESS_CONFIG_` nas variáveis individuais.

Os [providers oficiais](https://giftless.datopian.com/en/latest/auth-providers.html)
são JWT, GitHub e acesso anônimo. Não há cadastro nativo de usuários e senhas
HTTP Basic convencionais nessa release:

- O provider JWT aceita `Authorization: Bearer` e, para clientes Basic,
  aceita o token JWT como senha do usuário `_jwt`. Os scopes limitam
  organização, repositório, objeto e operações. Requer um emissor de tokens
  e uma chave de assinatura.
- O provider GitHub aceita PATs e tokens de instalação de GitHub Apps,
  verificando identidade e permissões do repositório no GitHub. Na
  [implementação v0.6.2](https://github.com/datopian/giftless/blob/v0.6.2/giftless/auth/github.py),
  a opção de restrição é `restrict_to`, por exemplo
  `{splor-mg: [datamart]}`. Depende de acesso à API GitHub e de permissões
  adequadas no token de cada cliente.
- Providers anônimos de leitura ou escrita servem para cenários limitados
  e testes; não resolvem a necessidade de acesso autenticado aos objetos.

Independentemente do provider de entrada, o Giftless usa
`PRE_AUTHORIZED_ACTION_PROVIDER` para assinar URLs de transferência. O
valor padrão da chave é `change-me`, portanto o laboratório deve fornecer
sua própria chave persistente por ambiente.

### Endpoints e proxy HTTPS

Com `LEGACY_ENDPOINTS: false`, o endpoint moderno tem o formato
`/<organização>/<repositório>.git/info/lfs`, por exemplo
`https://lfs.exemplo.gov.br/splor-mg/datamart.git/info/lfs`. O cliente deve
configurar `lfs.url`; o Giftless não implementa o fluxo de locking descrito
no Git LFS, e o quickstart orienta `git config lfs.locksverify false`.

Ao receber HTTP de um proxy que terminou HTTPS, o Giftless precisa conhecer
host e protocolo externos para gerar URLs de upload/download acessíveis.
O middleware `werkzeug.middleware.proxy_fix:ProxyFix` está instalado e pode
confiar em uma camada de `X-Forwarded-Proto`, `X-Forwarded-Host` e
`X-Forwarded-Port`. O proxy deve preencher esses headers corretamente; os
serviços devem ficar acessíveis pelo proxy confiável. Se houver prefixo de
caminho, avaliar também `X-Forwarded-Prefix`.

Fontes: [Runtime Configuration](https://giftless.datopian.com/en/latest/configuration.html)
e [Using WSGI Middleware](https://giftless.datopian.com/en/latest/wsgi-middleware.html).

## Easypanel

A [documentação oficial de App Service](https://easypanel.io/docs/services/app)
descreve origem por imagem Docker, variáveis de ambiente, configuração de
comando e argumentos, mounts de volume e arquivo, domínios com HTTPS e
seleção da porta interna do proxy. Esses elementos correspondem às
necessidades dos serviços: porta `3000` para Metabase, `8080` para Giftless
e volumes persistentes para PostgreSQL e objetos LFS.

Na pesquisa, a
[página oficial do Compose Service](https://github.com/easypanel-io/website/blob/main/docs/03-services/08-compose.md)
continha apenas `Documentation Coming Soon`. Não foi possível confirmar
pela documentação detalhes de importação de repositório, tratamento de
arquivos auxiliares, bind mounts e `depends_on` nessa modalidade. Esses
comportamentos devem ser verificados na versão instalada do Easypanel.
O Compose pode ser executado diretamente em um checkout do branch no host
Linux com Docker Compose; para serviços criados individualmente no painel,
é necessário reproduzir variáveis, volumes, script de inicialização e
conexões internas.

Não publicar PostgreSQL indiscriminadamente é coerente com a governança
pendente do Datamart. Para acesso remoto de ETL ou administração, definir
um túnel ou regras explícitas de IPs confiáveis. Para Metabase e Giftless,
usar domínios HTTPS e confirmar que as URLs devolvidas pelo batch LFS
apontam para o domínio público correto.

O requisito adicional do laboratório é permitir que desenvolvedores e
agentes acessem os três serviços sem uma conta no Easypanel. Somente o
Metabase possui interface web; PostgreSQL oferece SQL/TCP e Giftless
oferece Git LFS/HTTP. O [guia operacional](easypanel-labanca.md) descreve
endpoints, credenciais, API keys e publicação PostgreSQL com TLS por
**três App Services independentes**, com Dockerfiles em `docker/postgres`,
`docker/metabase` e `docker/giftless`. Em 22/10/2026, o usuário alterou o
pedido de Compose único para três serviços separados. O consolidado foi
removido; o Compose base e complemento TLS continuam para uso local.
As imagens incorporam scripts, evitando bind mounts de código no painel.
Cada Dockerfile usa a própria pasta como contexto de build, conforme o
campo **Caminho de Build** observado no Easypanel. Os `COPY` são relativos
a essa pasta, e o campo **Arquivo** permanece `Dockerfile` em cada serviço.
Certificados reais e firewall são configurações
do operador do servidor. A implementação usa JWT no Giftless com um
emissor executado pelo operador, além de chave separada para as URLs
temporárias de transferência.

Fontes adicionais: [API keys do Metabase](https://www.metabase.com/docs/latest/people-and-groups/api-keys)
e [TLS do PostgreSQL](https://www.postgresql.org/docs/17/ssl-tcp.html).

O [template oficial Directus do Easypanel](https://github.com/easypanel-io/templates/blob/main/templates/directus/index.ts)
usa `$(PROJECT_NAME)_NOME_DO_SERVICO` para `DB_HOST`. Metabase usa esse DNS
configurável em `MB_DB_HOST` e URI JDBC com TLS; confirme rede e hostname na
instalação de destino. A ordem PostgreSQL primeiro substitui `depends_on`
do Compose local, porque App Services são implantados individualmente.
