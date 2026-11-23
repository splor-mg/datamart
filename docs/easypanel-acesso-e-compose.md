# Acesso dos desenvolvedores e agrupamento dos serviços

Decisões e implantação iniciadas em 23/11/2026.
As fontes estão na [pesquisa](easypanel-acesso-contexto.md).

**Status: implantação em andamento.** Estão confirmados o acesso administrativo
completo às três ferramentas e à VM por SSH, a escolha do cliente/IA pelo
destinatário e a entrega dos serviços sem carga de dados. Não serão
fornecidos usuário e senha da interface do Easypanel. Também estão
confirmados o PostgreSQL interno separado para Metabase e a conta Linux
com chave SSH e `sudo` sem senha. A manutenção persistente dos serviços
usará a API/CLI oficial do painel, a validar nesta VM. A administração
Azure e a recuperação da VM ficam com o operador da plataforma. A chave
pública do destinatário ainda precisa ser fornecida para instalar seu acesso.
A conectividade SSH pela CAMG foi resolvida no projeto `azure-migration`,
com TCP/22 autorizado para a saída pública do proxy corporativo. O
[procedimento de acesso](acesso-ssh-camg.md) registra a regra aplicada,
o comando de conexão e o teste pela VPN que ainda está pendente.
Veja a [decisão de autonomia administrativa](adr/0001-autonomia-administrativa-do-laboratorio.md)
e o [vocabulário](../CONTEXT.md).

## Acesso do administrador do laboratório e suas ferramentas de IA

O destinatário terá administração plena das ferramentas e da VM por SSH.
Não será uma conta limitada a túnel, leitura SQL ou repositórios escolhidos
pelo operador. Não serão entregues usuário e senha do Easypanel. Isso não
isola tecnicamente o painel de quem administra a máquina que o hospeda.

| Recurso | Acesso decidido | Credencial ou mecanismo |
|---|---|---|
| VM do laboratório | Executar comandos e administrar a instalação, inclusive os containers | Conta própria, chave SSH e sudo sem senha |
| PostgreSQL | Administração da(s) instância(s) do laboratório, bancos, schemas, tabelas e usuários | Conta administrativa própria; comandos também disponíveis através da VM |
| Metabase | Administrador global e automação administrativa | Conta individual e API key do grupo Administrators |
| Giftless | Todas as operações LFS suportadas e administração da instalação | JWT amplo para a API; comandos/configurações pela VM |

A escolha de cliente, plataforma ou agente de IA é do administrador.
A entrega deve permitir execução de comandos e uso das APIs sem depender
atualmente do operador para cada alteração. O papel do agente não implica
uma restrição adicional de permissões nas ferramentas.

Giftless não tem uma API administrativa para todas as operações da
instalação. No adapter atual existem batch, upload, download e verificação;
configurações, armazenamento e emissão de tokens dependem de outros
mecanismos. O script `/app/create-token.py` pode ser executado pelo
administrador através da VM para emitir um token novo, sem login no painel.
Não há um endpoint de renovação HTTP implementado nesta preparação.
Giftless armazena os objetos LFS; o servidor dos commits Git é separado.

A identidade técnica do Metabase ao conectar ao seu banco interno permanece
separada da identidade administrativa do destinatário. A instância própria
para o banco interno foi confirmada no alinhamento.

Não serão aplicadas as restrições de shell e sudo da proposta anterior.
Chave SSH e execução de sudo sem senha foram confirmadas. Conectividade e
procedimentos de atualização persistente dos serviços serão validados antes
da implantação.
A documentação operacional precisa distinguir parâmetros gerenciados pelo
painel de alterações realizadas diretamente nos containers. A API oficial
do Easypanel oferece operações programáticas com token, inclusive para
atualizar ambiente e fonte Compose e reimplantar. A compatibilidade da CLI
com a versão instalada será validada antes de entregar esse mecanismo.

Senhas, chaves privadas e tokens serão mantidos fora do Git e dos prompts.
A forma de utilizá-los nos clientes/agentes também fica sob responsabilidade
do administrador, que poderá emitir e administrar suas credenciais.

## Metabase e seu PostgreSQL em um item Compose

Conforme a [decisão confirmada](adr/0002-postgresql-interno-do-metabase.md),
o arquivo [compose.metabase.yaml](../compose.metabase.yaml) agrupa dois
containers no item `metabase-compose` do projeto Easypanel:

- `metabase`: imagem oficial, HTTP na porta interna `3000`;
- `postgres`: banco da aplicação, sem porta publicada, com volume próprio
  e usuário `metabase` sem poderes de superusuário.

O PostgreSQL analítico `datamart-postgres` continua independente. Metabase
acessa seus próprios dados pela rede privada do Compose e acessa a fonte
analítica através da rede compartilhada do Easypanel. Giftless continua
como outro item, com volume em `/lfs-storage`. Assim, o projeto mantém os
três itens funcionais, mesmo com dois containers dentro de Metabase.

Antes de implantar o novo item:

1. Use `EASYPANEL_NETWORK=easypanel`, rede overlay attachable confirmada
   na VM em 23/11/2026. Tanto o proxy quanto o PostgreSQL analítico estão
   conectados a ela. Confirme novamente se a implantação mudar de VM.
2. Preencha [docker/metabase/.env.compose.example](../docker/metabase/.env.compose.example)
   no ambiente do item Compose e marque **Create .env file**. Sem essa
   opção o painel não disponibiliza as variáveis para interpolar o YAML.
   Preserve senhas e chave de criptografia
   entre deploys; as senhas iniciais são aplicadas apenas ao volume vazio.
3. Importe o conteúdo de `compose.metabase.yaml` em um item **Compose**.
   Associe o domínio HTTPS existente ao container `metabase`, porta `3000`.
   O proxy precisa compartilhar a rede informada com esse container.
4. Planeje a troca do item App atual pelo item Compose, sem apagar o H2 ou
   volumes existentes antes da validação. Na última conferência, a
   interface Metabase ainda estava no assistente inicial. Se houver novo
   conteúdo a preservar, faça a migração oficial de H2 antes da troca.
5. Valide `/api/health`, a criação de tabelas no banco interno, o assistente
   inicial e o acesso à base analítica. Confira os mounts do volume
   `metabase_db_data` no host para a política de backup.

Este arquivo é independente de `compose.yaml`, que mantém o laboratório
local com os três serviços. Não combine ambos como overlays. Para validar
o arquivo pelo terminal, com o ambiente preenchido:

```sh
docker compose -f compose.metabase.yaml \
  --env-file docker/metabase/.env.compose config --quiet
```

Não use `docker compose down -v` em uma instalação com dados: esse comando
remove o volume do banco interno. Alterar o nome do projeto Compose também
pode fazer o Docker escolher outro volume, em vez de reutilizar o existente.

### Validação desta preparação

Em 23/11/2026, o Compose foi importado e implantado na VM pelo Easypanel.
Foi necessário marcar **Create .env file** na tela Environment para
resolver as variáveis do YAML. O painel deu sucesso na implantação e
os dois containers ficaram `healthy`. A API `/api/health` respondeu
`{"status":"ok"}`; o banco interno apresentou 192 tabelas em `public`.
A verificação foi repetida após reiniciar o grupo: os dois containers
voltaram saudáveis e as 192 tabelas permaneceram no volume.
A role técnica `metabase` não é superusuária. Não há portas publicadas
nesse par de containers; a aplicação está nas redes privada e `easypanel`.

O volume do banco interno ficou em
`/var/lib/docker/volumes/datamart_metabase-compose_metabase_db_data/_data`.
O item App anterior `metabase` foi parado e seu volume H2 preservado.
Sua rota foi movida para `/previous-h2`, sem apagar dados. O novo domínio
ainda não foi associado à porta 3000: a publicação foi bloqueada pela
revisão automática enquanto o primeiro administrador não estiver criado.

No Giftless, foi criado o volume `lfs-storage`, montado em `/lfs-storage`.
Batch, upload, verify e download pela URL HTTPS passaram com um objeto
sintético no namespace `splor-mg/datamart-smoke`. O hash desse objeto foi
conferido após reiniciar o serviço, confirmando a persistência. Não houve carga SIAFI
ou Linktable. O Metabase privado também respondeu ao healthcheck a partir
do container Giftless.

### Criar o primeiro administrador antes de publicar

Execute [initialize-admin.py](../docker/metabase/initialize-admin.py)
em um terminal interativo da VM:

```sh
python3 docker/metabase/initialize-admin.py
```

O comando usa `docker exec` para alcançar o Metabase privado. Se o login
Linux precisar de sudo para acessar Docker, execute com `sudo python3`.
Ele solicita nome, e-mail e senha; a senha não aparece no terminal, nos
argumentos dos processos nem no histórico. O administrador executa e
confirma a criação pessoalmente. O comando recusa execução por pipe,
recusa URL pública e não altera uma instalação que já concluiu o setup.

Para a primeira configuração pelo painel, uma cópia temporária do script
foi preparada no container Giftless. Abra a **Console** desse item e rode:

```sh
python /tmp/initialize-metabase-admin.py \
  --url http://datamart_metabase-compose-metabase-1:3000
```

Essa cópia em `/tmp` não é persistente; o arquivo versionado é a referência.
O script passou em Ruff 0.14.10, validação de sintaxe Python e teste da
recusa de entrada de credenciais por pipe. A criação da conta continua
dependendo da execução e confirmação pessoal do administrador.
Depois da mensagem de sucesso, confira que `setup-token` ficou vazio na
API de propriedades da sessão. Então associe o domínio HTTPS existente ao
Compose Service `metabase`, porta `3000`, e entre com a conta criada.
O item H2 anterior só será excluído definitivamente após confirmação.

### Comandos SQL com a administração SSH

Entre na VM pelo [proxy da CAMG](acesso-ssh-camg.md), usando sua conta
Linux e chave autorizadas. Na sessão SSH, execute:

```sh
PG_CONTAINER="$(sudo docker ps -q \
  --filter label=com.docker.swarm.service.name=datamart_datamart-postgres)"
sudo docker exec -it "$PG_CONTAINER" psql -U postgres -d datamart
```

Isso permite administrar bancos, schemas e roles sem abrir PostgreSQL
na Internet. O administrador também pode executar scripts SQL com
`docker exec -i` e usar os comandos por um agente remoto. Para uma GUI
SQL local, valide um destino privado alcançável pela VM antes de configurar
um túnel; os nomes DNS dos containers não são automaticamente resolvidos
pelo host. A chave SSH autentica a VM, não substitui login HTTP do Metabase
ou autenticação Git LFS.

### CLI oficial do Easypanel

A [CLI oficial](https://easypanel.io/docs/cli) foi instalada na VM em
`/usr/local/bin`, pelos comandos abaixo. O instalador verificou o checksum
SHA-256 do binário. A versão conferida foi `0.1.4`.

```sh
curl -fsSL https://get.easypanel.io/cli | sh
easypanel version
```

O Azure Run Command executa sem um contexto de login completo. A CLI
precisa de um diretório de usuário; sua execução foi validada por
`sudo -H -u aidadmin easypanel version`. Em uma sessão SSH normal, use a
conta Linux que receberá a administração.

A conexão autenticada ainda está pendente: o binário instalado não implica
que uma API key ou o manifesto de comandos do servidor estejam validados.
Na entrega, configure um perfil com a API key autorizada, sem registrar o
token no Git ou no chat:

```sh
easypanel server add datamart-lab https://h0ydxp.easypanel.host
easypanel server check datamart-lab
easypanel projects list --format json
easypanel --help
```

O primeiro comando solicita a chave sem exibi-la. Conforme a documentação,
a CLI usa Secret Service no Linux para guardar credenciais; confira a
disponibilidade desse mecanismo na VM headless. Para automação, a CLI
também aceita `EASYPANEL_API_KEY` no ambiente do processo. Use um arquivo
protegido/gerenciador de segredos, sem incluir o valor no comando ou prompt
do agente. Os comandos de gestão são fornecidos pelo servidor; confirme
os nomes com `--help` antes de criar scripts de deploy.

### Pendências para concluir a entrega

- Receber a chave pública e criar o login `datamart-admin`, com chave SSH
  e sudo sem senha, conforme decidido. A conectividade pela CAMG como
  `aidadmin` foi confirmada no `azure-migration`; falta testar a conta
  do destinatário. O acesso pela VPN de casa também está pendente.
- Concluir pessoalmente o assistente privado do administrador Metabase e
  só então associar o domínio HTTPS existente ao container `metabase:3000`.
- Configurar e validar a autenticação da CLI/API para manutenção persistente.
- Excluir o item App H2 anterior após validar a troca e confirmar a exclusão.
- Entregar os comandos e credenciais do laboratório por canal privado.
  A carga e a organização dos dados ficarão a cargo do destinatário.

## Origem dos schemas do Datamart

O [comentário do Datamart #26](https://github.com/splor-mg/datamart/issues/26#issuecomment-5996515573)
propõe exemplos de carga `dpetl_load` com `target: postgres`, usando
`schema: dados_siafi` para SIAFI e `schema: linktable` para a Linktable,
além de `PG_URL`, `COPY` e transação. O
[issue Projetos #24](https://github.com/splor-mg/projetos/issues/24#issuecomment-6317664618)
pede uma instância de teste com dados SIAFI, Metabase e avaliação de acesso.

Esses nomes vêm da proposta ETL, não de uma exigência do template
PostgreSQL nem das migrations Django atuais. O script
`docker/postgres/init-databases.sh` criou esses schemas como uma escolha de
implementação do laboratório. Os templates nativos não executaram esse
script. Na conferência de 23/11/2026, o banco `datamart` tinha `public` com
zero tabelas e não tinha os dois schemas. A estrutura e a carga dos dados
ficarão a cargo do administrador do laboratório; a entrega atual não inclui
carga SIAFI, Linktable ou implantação de um pipeline analítico.

## Como considerar o backup Azure existente

A ausência de backups na tela do Easypanel não prova ausência de backup
da VM. O backup Azure pode proteger os dados persistentes quando todos os
discos e caminhos relevantes estão incluídos. Um backup consistente em
nível de sistema de arquivos também pode permitir recuperação PostgreSQL
com seus arquivos de dados e WAL completos; o teste de restauração é o que
confirma a recuperabilidade desse ambiente.

Na VM `vm-aid-runtime-dev`, o backup estava habilitado no vault
`rsv-aid-prd`, política `policy-vm-daily (Enhanced)`, com todos os discos
incluídos. A última execução consultada foi bem-sucedida em 23/11/2026;
havia 30 pontos consistentes em nível de sistema de arquivos.

Foram conferidos Docker data-root `/var/lib/docker` e os mounts:

| Dados | Caminho persistente na VM |
|---|---|
| PostgreSQL analítico | `/etc/easypanel/projects/datamart/datamart-postgres/data` |
| PostgreSQL do Metabase | `/var/lib/docker/volumes/datamart_metabase-compose_metabase_db_data/_data` |
| Giftless | `/var/lib/docker/volumes/datamart_giftless_lfs-storage/_data` |
| H2 anterior, preservado | `/var/lib/docker/volumes/datamart_metabase_data/_data` |

Esses caminhos ficam no disco de SO `/dev/root`, não no disco temporário
Azure. O backup da VM cobre esse disco; os volumes recém-criados entrarão
nos próximos snapshots. A persistência continua necessária mesmo com
backup da VM. Não foi criado recurso Azure adicional nesta implantação.
As metas confirmadas são RPO de até 24 horas de perda de dados e RTO de
até um dia útil de recuperação. São metas a validar com o backup existente,
e não garantias já demonstradas. Teste a restauração em ambiente isolado,
sem substituir a VM em uso. Dumps SQL ou backup PostgreSQL/PITR são complementos
para recuperação granular ou RPO menor; não são uma duplicação obrigatória
apenas porque o painel mostra uma lista vazia de backups.
