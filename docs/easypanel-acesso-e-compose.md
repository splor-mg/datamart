# Acesso dos desenvolvedores e agrupamento dos serviços

Proposta preparada em 23/11/2026, antes de alterar os serviços em execução.
As fontes estão na [pesquisa](easypanel-acesso-contexto.md).

## Acesso de um desenvolvedor e suas ferramentas de IA

O desenvolvedor recebe credenciais dos serviços, sem conta de operador do
Easypanel e sem credenciais administrativas da VM/Docker. A proposta é:

| Serviço | Acesso | Credencial e limite |
|---|---|---|
| PostgreSQL analítico | Cliente SQL, através de VPN existente ou túnel SSH restrito | Role individual no `datamart`, com permissões de desenvolvimento combinadas com a equipe |
| Metabase | Domínio HTTPS, navegador e API | Conta individual e grupo de permissões; para automação, API key vinculada ao grupo |
| Giftless | Domínio HTTPS, Git LFS e API HTTP | JWT com prazo de validade e scopes limitados ao repositório autorizado |

A chave SSH autentica o túnel. Ela não substitui o usuário SQL, a conta/API
key do Metabase nem o JWT do Giftless. Os serviços HTTP já dispõem de HTTPS
pelo proxy do Easypanel, portanto não precisam passar pelo túnel para uso
normal. O banco de configuração do Metabase é interno e não será entregue
ao desenvolvedor.

Se não houver VPN institucional adequada, use uma conta SSH exclusiva para
port forwarding: sem sudo, shell interativo, acesso ao Docker, painel,
agent forwarding ou encaminhamento a outros destinos. Cadastre uma chave
por pessoa/dispositivo, com a chave privada somente no computador do
usuário. O operador configura `PermitOpen` para o destino SQL permitido,
`AllowTcpForwarding local` e bloqueia sessões/comandos com `MaxSessions 0`.
`restrict` em `authorized_keys` sozinho não bloqueia shell. Um trecho a
adaptar e validar pelo operador no `sshd_config` é:

```text
Match User USUARIO_TUNEL
    AuthenticationMethods publickey
    PasswordAuthentication no
    AllowTcpForwarding local
    AllowStreamLocalForwarding no
    PermitOpen 127.0.0.1:15432
    AllowAgentForwarding no
    X11Forwarding no
    PermitTTY no
    PermitTunnel no
    GatewayPorts no
    MaxSessions 0
Match all
```

Isso não cria a conta, publica a porta SQL ou instala a chave. A
configuração e sua validação ainda pertencem à etapa de implantação.

Um exemplo de uso, **depois de preparar o destino restrito na VM**, é:

```sh
ssh -N -T -o ExitOnForwardFailure=yes \
  -L 127.0.0.1:15432:127.0.0.1:15432 \
  -i /caminho/chave_privada USUARIO_TUNEL@HOST_DA_VM
```

O cliente SQL usa então `127.0.0.1:15432`, com sua credencial individual.
O servidor SSH precisa alcançar o PostgreSQL em seu próprio
`127.0.0.1:15432`. Isso ainda não está preparado: o serviço nativo observado
está sem porta publicada. Não use o DNS Docker
`datamart_datamart-postgres` como se ele resolvesse no host SSH.

Ao implantar, prefira uma publicação em loopback. Se o serviço nativo só
permitir publicar em todas as interfaces, prepare antes NSG/firewall para
impedir acesso externo à porta SQL, permitindo somente o caminho previsto
da VPN/túnel. Não publique PostgreSQL para a Internet como requisito do
acesso SSH. Confirme o resultado de dentro e de fora da rede autorizada.

Para IA executada no computador do usuário, use o túnel e os credential
helpers/variáveis de ambiente locais. Para um agente executado na nuvem,
é preciso autorizar separadamente sua origem de rede e fornecer credenciais
limitadas pelo mecanismo de segredos dessa plataforma. Chaves privadas,
senhas e tokens não entram em prompts, arquivos versionados ou logs. A
chave de assinatura JWT do Giftless permanece com o operador; o usuário
recebe apenas tokens emitidos para ele.

## Metabase e seu PostgreSQL em um item Compose

O arquivo [compose.metabase.yaml](../compose.metabase.yaml) agrupa dois
containers no item `metabase` do projeto Easypanel:

- `metabase`: imagem oficial, HTTP na porta interna `3000`;
- `postgres`: banco da aplicação, sem porta publicada, com volume próprio
  e usuário `metabase` sem poderes de superusuário.

O PostgreSQL analítico `datamart-postgres` continua independente. Metabase
acessa seus próprios dados pela rede privada do Compose e acessa a fonte
analítica através da rede compartilhada do Easypanel. Giftless continua
como outro item, com volume em `/lfs-storage`. Assim, o projeto mantém os
três itens funcionais, mesmo com dois containers dentro de Metabase.

Antes de implantar o novo item:

1. Confirme a rede Docker compartilhada pelo projeto e pelo proxy.
   `EASYPANEL_NETWORK` é obrigatório: o nome exato não foi inferido pelo
   nome do projeto nem confirmado na documentação do Compose do painel.
2. Preencha [docker/metabase/.env.compose.example](../docker/metabase/.env.compose.example)
   no ambiente do item Compose. Preserve senhas e chave de criptografia
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

Em 23/11/2026, `docker compose config` validou a estrutura, as redes e a
ausência de portas publicadas. O bootstrap foi verificado com shell Bash:
sintaxe, geração do arquivo de inicialização e passagem do comando
`postgres` ao entrypoint. Os arquivos de teste temporários foram removidos.
O engine Docker local não respondeu, portanto os testes de inicialização,
healthchecks e persistência do novo par de containers ainda precisam ser
executados antes da implantação. Também falta confirmar a rede do
Easypanel e validar a importação nessa instalação do painel.

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
zero tabelas e não tinha os dois schemas. A estrutura deve ser confirmada
com o pipeline/dataset selecionado antes de criá-la e carregar dados.

## Como considerar o backup Azure existente

A ausência de backups na tela do Easypanel não prova ausência de backup
da VM. O backup Azure pode proteger os dados persistentes quando todos os
discos e caminhos relevantes estão incluídos. Um backup consistente em
nível de sistema de arquivos também pode permitir recuperação PostgreSQL
com seus arquivos de dados e WAL completos; o teste de restauração é o que
confirma a recuperabilidade desse ambiente.

Confirme os caminhos de Docker/volumes, dados PostgreSQL e WAL no host,
incluindo se algo está em disco temporário ou armazenamento externo. A
persistência em volume continua necessária mesmo com backup da VM.
Defina o RPO/RTO esperado e teste a restauração em ambiente isolado, sem
substituir a VM em uso. Dumps SQL ou backup PostgreSQL/PITR são complementos
para recuperação granular ou RPO menor; não são uma duplicação obrigatória
apenas porque o painel mostra uma lista vazia de backups.
