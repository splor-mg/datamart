# Fontes para acesso, schemas e backup do laboratório

O acesso limitado descrito nesta pesquisa foi substituído pela
[decisão de administração completa](adr/0001-autonomia-administrativa-do-laboratorio.md).
Use o [guia operacional atual](easypanel-acesso-e-compose.md) para implantar.
As fontes e a distinção entre requisito e proposta continuam como referência.

Pesquisa em 23/11/2026. Este registro fundamenta a proposta de acesso e
separa requisitos dos projetos, escolhas de implementação e verificações
que ainda dependem do ambiente. Não houve criação de contas, concessão de
permissões ou acesso à Azure pelo agente de pesquisa.

## Acesso sem uma conta no Easypanel

Uma chave SSH autentica um acesso SSH ou túnel; ela não substitui a
autenticação SQL, a conta Metabase nem o token HTTP do Giftless. A proposta
é fornecer credenciais individuais por finalidade:

| Serviço | Acesso proposto | Credencial do usuário/agente |
|---|---|---|
| PostgreSQL analítico | SQL pela rede privada/VPN ou túnel SSH restrito | Role `LOGIN` dedicada, limitada ao banco e schemas autorizados |
| Metabase | Domínio HTTPS existente | Conta individual por grupo e API key associada a grupo para automação |
| Giftless | Git LFS/API pelo domínio HTTPS existente | JWT com prazo e scopes limitados à organização/repositório |

O banco interno PostgreSQL do Metabase guarda a configuração da aplicação;
não é o banco que se entrega ao desenvolvedor para desenvolver ETL ou
consultar dados analíticos. A identidade da aplicação deve permanecer
separada da identidade do usuário.

O [Metabase define os direitos da API key pelo grupo associado](https://www.metabase.com/docs/latest/people-and-groups/api-keys)
e aceita `X-API-Key` nas requisições. Não é necessário conceder o grupo
Administrators para criar perguntas ou painéis em coleções autorizadas.
As ações permitidas devem corresponder ao trabalho do desenvolvedor.

O [provider JWT do Giftless v0.6.2](https://github.com/datopian/giftless/blob/v0.6.2/docs/source/auth-providers.md#jwt-authenticator)
aceita `Authorization: Bearer` e JWT como senha do usuário Basic `_jwt`.
Os scopes permitem limitar organização, repositório, objetos e operações
`read`, `write`, `verify`, por exemplo `obj:splor-mg/REPO/*:read,write,verify`.
A chave de assinatura permanece com o operador; o desenvolvedor recebe o
token, não essa chave. Git sobre SSH e Git LFS sobre HTTPS são acessos
distintos; o provider GitHub também não autentica LFS por chave SSH.

Para um túnel SSH, a conta não deve ter `sudo`, acesso ao socket/grupo
Docker ou shell administrativo na VM que hospeda todos os serviços.
Permitir apenas o destino SQL evita transformar um túnel em acesso à
infraestrutura do Easypanel. O [manual oficial OpenSSH](https://man.openbsd.org/sshd.8#AUTHORIZED_KEYS_FILE_FORMAT)
documenta `permitopen="host:port"`, `restrict`, `port-forwarding` e comandos
forçados. O [sshd_config](https://man.openbsd.org/sshd_config.5) documenta
`AllowTcpForwarding local`, `PermitOpen`, `PermitTTY` e `ForceCommand`.
**`restrict` sozinho não impede shell/comandos**: também é necessário
negar a execução de sessões, por configuração/command forçado apropriado.

O destino do túnel deve ser alcançável por onde o SSH servidor roda. O DNS
Docker `datamart_datamart-postgres` normalmente é resolvido pelos containers
da rede, não pelo host da VM. Antes de entregar um comando SSH, confirmar
um endpoint loopback/private no host ou um bastion limitado conectado à
rede Docker. Não publicar PostgreSQL na Internet para fazer o túnel funcionar.

Para agentes de IA, entregar somente os direitos necessários à tarefa,
guardar credenciais em variáveis/credential helpers fora do Git e usar
tokens separados quando for necessário revogar/auditar automações.

## Origem dos schemas e das tabelas

O [comentário do Datamart #26 de 05/10/2026](https://github.com/splor-mg/datamart/issues/26#issuecomment-5996515573)
é a origem explícita dos **dois nomes**:

- `dpetl_load.target: postgres`, com `schema: dados_siafi` como exemplo de
  namespace para resources SIAFI;
- Linktable gravada no schema `linktable`, herdando o destino dos pacotes
  de origem;
- conexão `PG_URL`, tabelas derivadas dos schemas Frictionless, carga
  `COPY` e atualização transacional.

O próprio comentário chama essa configuração de **proposta** e indica que
`schema` do load é opcional. Portanto, `dados_siafi` e `linktable` são a
organização prevista para esse fluxo ETL; não são exigências do template
PostgreSQL ou do Metabase. Os scripts do laboratório os criaram para
acomodar essa proposta.

O [comentário Projetos #24 de 21/10/2026](https://github.com/splor-mg/projetos/issues/24#issuecomment-6317664618)
pede uma instância de teste PostgreSQL, sugere dados SIAFI, conexão
Metabase e exploração dos níveis de acesso. Ele não exige esses dois
nomes de schema. A estrutura das tabelas deve vir do fluxo de dados
escolhido e dos seus descriptors/migrations, em vez de ser inventada na
configuração do Easypanel.

No código atual do Datamart, [`datamart/settings.py`](../datamart/settings.py)
configura o banco por `DB_NAME`, usuário, senha, host e porta. A pesquisa no
código de modelos/migrations não encontrou `search_path` nem `db_table`
que obrigue esses schemas SQL. A necessidade de executar migrations Django
é diferente da carga dos resources ETL em `dados_siafi`/`linktable`.

Um [comentário posterior no Projetos #24](https://github.com/splor-mg/projetos/issues/24#issuecomment-6452292543)
descreve [metabase-siafi-teste](https://github.com/LorenadeCastro/metabase-siafi-teste):
oito tabelas de [dados-siafi-2026](https://github.com/splor-mg/dados-siafi-2026),
DDL derivado de `datapackage.json`, usuários separados e views agregadas
num schema `painel`. É uma referência adicional de teste, posterior à
pesquisa de outubro; não torna automaticamente suas oito tabelas e nomes
um requisito da implantação atual.

## Compose e conexão ao PostgreSQL analítico existente

Metabase e seu PostgreSQL interno podem formar um Compose próprio,
mantendo o PostgreSQL analítico existente separado. O Postgres interno da
aplicação não precisa de uma porta publicada no host nem de uma conexão
externa para o usuário.

O [template oficial Directus](https://github.com/easypanel-io/templates/blob/main/templates/directus/index.ts)
comprova o padrão de hostname `$(PROJECT_NAME)_NOME_DO_SERVICO` usado para
conexões entre serviços nativos. Isso não comprova o nome da rede Docker
compartilhada ou seu atributo `attachable`.

A [página oficial de Compose](https://github.com/easypanel-io/website/blob/main/docs/03-services/08-compose.md)
consultada ainda contém `Documentation Coming Soon`. Para conectar o novo
Compose ao PostgreSQL analítico e ao proxy existentes, conferir a rede
real do ambiente; uma variável `EASYPANEL_NETWORK` evita assumir que ela
se chama `easypanel`. A rede externa só deve ser adicionada ao container
Metabase que precisa consultar dados; o banco interno pode ficar na rede
privada do par.

## Azure Backup já ativado

O relato do usuário de backup Azure ligado é compatível com não haver
backups registrados nas telas internas do Easypanel. São camadas diferentes.
Não se deve concluir que a VM está sem backup apenas pela lista vazia do
painel de banco/volume.

Na [visão geral Azure VM Backup](https://learn.microsoft.com/en-us/azure/backup/backup-azure-vms-introduction#snapshot-consistency),
Linux sem scripts de aplicação usa normalmente snapshot consistente com
o filesystem. Application-consistent em Linux depende dos scripts
pre/post apropriados. Crash-consistent também é uma modalidade suportada,
e a recuperação depende dos mecanismos de correção da aplicação.
O [framework Linux de scripts](https://learn.microsoft.com/en-us/azure/backup/backup-azure-linux-app-consistent)
permite preparar a aplicação para o snapshot; Azure apenas executa os
scripts configurados pelo operador, que responde por sua consistência.

O [PostgreSQL admite snapshot consistente de filesystem com o servidor rodando](https://www.postgresql.org/docs/17/backup-file.html):
a restauração faz recuperação de crash usando WAL. É necessário incluir
o cluster completo e os WALs; se dados, WAL e tablespaces se distribuem por
volumes, os snapshots devem ser simultâneos. Portanto, backup de VM pode
ser uma proteção válida de PostgreSQL, quando esses requisitos e a
restauração são verificados. Não é inerentemente inválido por ser snapshot.

O [Azure permite incluir/excluir discos](https://learn.microsoft.com/en-us/azure/backup/selective-disk-backup-restore).
Cada recovery point contém somente os discos incluídos. Precisam estar
incluídos os discos que realmente armazenam os diretórios de dados
PostgreSQL, WAL e volumes persistentes Giftless/Metabase, incluindo o
Docker data-root se os volumes estiverem ali. Um volume persistente ainda
é necessário: backup da VM não impede perda dos arquivos na substituição
de um container sem mount.

Antes de considerar o backup encerrado, conferir no portal: proteção da VM
correta, política/frequência/retenção, último job e recovery point válidos,
tipo de consistência e discos incluídos. Depois, testar restauração numa
VM isolada. `pg_dump`/`pg_restore` podem complementar snapshots para
restaurar um banco de forma granular; arquivamento WAL/PITR atende metas
mais finas de ponto de recuperação. Essa necessidade depende de RPO/RTO,
não deve ser assumida como duplicação obrigatória de tudo.
