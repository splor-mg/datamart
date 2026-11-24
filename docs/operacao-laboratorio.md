# Entrega e operação do laboratório Datamart

Configuração concluída em 23/11/2026 na VM `vm-aid-runtime-dev`, projeto
Easypanel `datamart`. Este é o guia para o administrador e seu agente de IA.
O administrador pode executar comandos, alterar configurações e administrar
as três ferramentas, usando SSH com `sudo` sem senha e a CLI autenticada.
A administração Azure e a recuperação da VM ficam com o operador da plataforma.

Uma cópia deste guia está na VM em
`/home/datamart-admin/LEIA-ME-laboratorio.md`. A referência versionada é o
[guia no branch easypanel-labanca](https://github.com/splor-mg/datamart/blob/easypanel-labanca/docs/operacao-laboratorio.md).

## Endereços e identidades

| Recurso | Endereço / identificação | Acesso |
|---|---|---|
| VM | `vm-aid-runtime-dev.brazilsouth.cloudapp.azure.com:22` | SSH como `datamart-admin`, via proxy CAMG |
| PostgreSQL analítico | Banco `datamart`; DNS Docker `datamart_datamart-postgres:5432` | SQL administrativo como `postgres`; shell ou túnel SSH |
| Metabase | <https://datamart-metabase.h0ydxp.easypanel.host> | Administrador global e API key do grupo `Administrators` |
| Giftless | <https://datamart-giftless.h0ydxp.easypanel.host> | Git LFS/API com JWT; configuração e emissão de tokens por SSH |
| Gestão dos serviços | `lab-easypanel`, executado na VM | Perfil `datamart-lab`, token administrativo da dev |

O Metabase tem interface web. PostgreSQL usa clientes SQL, como DBeaver,
pgAdmin ou `psql`; não foi adicionada uma interface web de banco. Giftless
é uma API Git LFS, sem painel web administrativo: um `404` na raiz do domínio
é esperado. A chave SSH autentica a VM; Metabase e Giftless usam suas
credenciais HTTP próprias.

A instalação Metabase chama-se **Datamart SPLOR**. A conta global criada
pelo responsável é `raiane.souza@planejamento.mg.gov.br`; a senha foi
definida pessoalmente e deve ser entregue pelo responsável por canal privado.
O banco analítico aparece no Metabase como **Datamart**, ID `2`.
A fonte **Sample Database** é a demonstração SQLite incluída no produto;
o banco interno do Metabase é PostgreSQL.

## Credenciais e strings de conexão

Na sessão SSH de `datamart-admin`, o arquivo consolidado fica em:

```text
/home/datamart-admin/.config/datamart/acessos.json
```

Ele contém endereços, usuário/senha SQL, URIs PostgreSQL completas para a
rede Docker e para o túnel local, a API key Metabase e a referência ao perfil
Easypanel. É um arquivo secreto, modo `600`, pertencente a `datamart-admin`.
O agente pode consumir esses arquivos durante a execução dos comandos;
não copie seu conteúdo para Git, tickets ou prompts.

| Arquivo na VM | Conteúdo |
|---|---|
| `~/.config/datamart/acessos.json` | Compilação de acesso e URIs SQL |
| `~/.config/datamart/postgres-admin.json` | Credenciais `postgres`, superusuário da instância analítica |
| `~/.config/datamart/postgres-analytics.json` | Role `datamart`, proprietária do banco, usada pela conexão do Metabase |
| `~/.config/datamart/metabase-api-key.json` | URL e chave **Laboratorio - automacao**, grupo `Administrators` |
| `~/.config/easypanel/credentials.json` | Credencial administrativa da CLI, perfil `datamart-lab` |

O formato da URI para um cliente SQL local é:

```text
postgresql://postgres:SENHA_URL_ENCODED@127.0.0.1:15432/datamart?sslmode=disable
```

O campo `postgres_admin.uri_ssh_tunnel` do arquivo consolidado já tem a
senha escapada corretamente. `postgres_metabase_datasource` contém a
identidade técnica separada usada pelo Metabase. Para atualizar a compilação
depois de atualizar os arquivos de credenciais:

```sh
lab-connection-info
```

Esse comando compila os arquivos existentes; não troca senhas nem tokens.
Ao rotacionar credenciais, atualize os clientes e esses arquivos também.
O token anterior da API Easypanel **dev** foi substituído nesta entrega;
clientes que o utilizavam precisam da nova credencial. O login web existente
permanece com a senha do responsável.

## Entrar na VM e executar comandos

Siga o [procedimento SSH CAMG](acesso-ssh-camg.md). É necessário alcançar
`proxycamg.prodemge.gov.br:8080`, usando sua autenticação corporativa.
Na rede externa, conecte a VPN corporativa antes. A chave pública instalada
é ED25519, fingerprint
`SHA256:HDb9ELZoNI1Mp9R62k7A+TXw24yAF/jsobpZyB8ObLU`.
Use a chave privada correspondente; cada destinatário pode instalar sua
própria chave pública depois de entrar com o acesso autorizado.

No Git Bash, com `ssh` e `connect` disponíveis:

```bash
(
  CAMG_PROXY_USER=SEU_USUARIO_CAMG
  LAB_SSH_KEY="$HOME/.ssh/SUA_CHAVE_PRIVADA"
  read -rsp 'Senha do proxy CAMG: ' HTTP_PROXY_PASSWORD
  printf '\n'
  export HTTP_PROXY_PASSWORD
  ssh -i "$LAB_SSH_KEY" -o IdentitiesOnly=yes \
    -o "ProxyCommand=connect -H ${CAMG_PROXY_USER}@proxycamg.prodemge.gov.br:8080 %h %p" \
    datamart-admin@vm-aid-runtime-dev.brazilsouth.cloudapp.azure.com
)
```

Na VM, confira o acesso e os serviços:

```sh
sudo -n id -u
lab-easypanel server check datamart-lab
sudo docker ps --filter name=datamart
lab-postgres -Atc 'SELECT current_user, current_database();'
lab-metabase-api GET /api/health
```

`sudo -n id -u` deve retornar `0`. `lab-postgres` abre `psql` como
superusuário `postgres`; permite administrar a instância inteira, bancos,
roles, schemas e tabelas. Para carregar um arquivo SQL sem interação:

```sh
lab-postgres -v ON_ERROR_STOP=1 < carga.sql
```

## Cliente SQL local por túnel SSH

Não há porta PostgreSQL publicada na Internet. O cliente local se conecta
à porta `15432` de sua própria máquina; o SSH protege o trajeto até a VM.
O auxiliar descobre o IP privado atual do container em `docker_gwbridge`.
Não use o DNS Docker como destino resolvido pelo host da VM.

No Git Bash, deixe este comando executando enquanto usar o cliente SQL:

```bash
(
  CAMG_PROXY_USER=SEU_USUARIO_CAMG
  LAB_SSH_KEY="$HOME/.ssh/SUA_CHAVE_PRIVADA"
  read -rsp 'Senha do proxy CAMG: ' HTTP_PROXY_PASSWORD
  printf '\n'
  export HTTP_PROXY_PASSWORD
  remote=datamart-admin@vm-aid-runtime-dev.brazilsouth.cloudapp.azure.com
  ssh_args=(-i "$LAB_SSH_KEY" -o IdentitiesOnly=yes
    -o "ProxyCommand=connect -H ${CAMG_PROXY_USER}@proxycamg.prodemge.gov.br:8080 %h %p")
  target="$(ssh "${ssh_args[@]}" "$remote" 'sudo -n lab-postgres-tunnel-target')" || exit
  ssh "${ssh_args[@]}" -N -o ExitOnForwardFailure=yes \
    -L "127.0.0.1:15432:${target}:5432" "$remote"
)
```

No DBeaver/pgAdmin/psql, use host `127.0.0.1`, porta `15432`, banco
`datamart` e as credenciais `postgres_admin`. O PostgreSQL nativo não usa
TLS nesta conexão privada; selecione SSL desabilitado. O certificado
Let's Encrypt dos domínios HTTPS protege Metabase/Giftless, não o protocolo
SQL. Se o container PostgreSQL for recriado, encerre e reabra o túnel para
descobrir seu novo endereço. A conexão TCP e a autenticação administrativa
no destino privado foram testadas; o túnel externo depende do teste do
destinatário com a rede CAMG/VPN e a chave correspondente.

## Metabase pela interface e pela API

O login global pode alterar configurações, conectar bancos, gerir usuários,
permissões, perguntas e dashboards. A chave administrativa oferece
automação sem enviar a senha de login ao agente.

O auxiliar lê a chave do arquivo privado e envia o header `X-API-Key`:

```sh
lab-metabase-api GET /api/database
lab-metabase-api GET /api/user/current
lab-metabase-api POST /api/dataset --input consulta.json
```

Exemplo de `consulta.json` para validar o banco entregue:

```json
{
  "database": 2,
  "type": "native",
  "native": {"query": "SELECT current_user, current_database()"},
  "parameters": []
}
```

O auxiliar aceita `GET`, `POST`, `PUT`, `DELETE` e JSON de arquivo ou stdin
(`--input -`). Consulte a [documentação API Metabase](https://www.metabase.com/docs/v0.64/api)
para a operação desejada. A API não tem versionamento estável separado:
confira os endpoints ao atualizar o produto. Respostas de operações de
credenciais devem ser gravadas em arquivos privados, não nos logs do agente.

## Giftless e Git LFS

Na VM, emita um JWT amplo com oito horas de validade:

```sh
umask 077
lab-giftless-token --subject SEU_USUARIO --hours 8 \
  > "$HOME/.config/datamart/giftless.jwt"
```

O token contém `obj:*/*/*:read,write,verify` e permite operar todos os
namespaces da instalação. O administrador pode emitir outro quando expirar,
sem depender do responsável pelo Easypanel. O parâmetro `--subject` identifica
o usuário. Para emitir um token adicional de escopo específico, use o
script `/app/create-token.py` no container.

No repositório Git do usuário, substitua `ORG/REPO` pelos nomes escolhidos:

```sh
git lfs install --local
git config --local lfs.url \
  https://datamart-giftless.h0ydxp.easypanel.host/ORG/REPO.git/info/lfs
git lfs track '*.parquet'
git add .gitattributes
```

O cliente Git LFS usa autenticação Basic: usuário `_jwt`, senha igual ao
JWT. Entregue o token por arquivo/canal privado e use o gerenciador de
credenciais do cliente. Não inclua o token na URL nem versione arquivos
com ele. Para clientes API, use `Authorization: Bearer TOKEN` e o endpoint
`/ORG/REPO.git/info/lfs/objects/batch`.

Giftless guarda os arquivos LFS. O remoto dos commits Git, por exemplo
GitHub, é configurado separadamente e exige suas próprias permissões.
Configuração, armazenamento e emissão de tokens são administrados na VM;
não existe endpoint administrativo completo ou renovação HTTP automática.

## Alterar configurações e implantar de forma persistente

Os auxiliares estão instalados em `/usr/local/bin`; seus fontes estão em
[scripts/lab](../scripts/lab). A CLI oficial `0.1.4` foi validada contra
Easypanel `2.33.2`, com 367 operações, usando backend de credenciais em
arquivo. O administrador não precisa de usuário/senha da interface do painel.

```sh
lab-easypanel postgres inspect datamart/datamart-postgres
lab-easypanel app inspect datamart/giftless
lab-easypanel compose inspect datamart/metabase-compose
lab-easypanel app update-env --help
lab-easypanel compose update-env --help
lab-easypanel compose update-source-inline --help
lab-easypanel postgres update-advanced --help
```

Consulte `--help` da operação para o JSON/campos exigidos pelo manifesto
da versão instalada. Use arquivos protegidos e `--input @arquivo.json`
quando houver segredos. Depois de salvar ambiente/fonte, implante pelo painel:

```sh
lab-easypanel app deploy datamart/giftless
lab-easypanel compose deploy datamart/metabase-compose
```

Giftless usa o branch `easypanel-labanca`, contexto `docker/giftless`.
Metabase usa a fonte Compose inline baseada em
[compose.metabase.yaml](../compose.metabase.yaml). Preserve seu ambiente,
a opção **Create .env file**, as senhas e a chave de criptografia entre
deploys. Mantenha o alias `datamart_metabase-compose_metabase` para o proxy.
Editar um container em execução não atualiza a fonte do Easypanel; a mudança
deve ser salva na configuração gerenciada para sobreviver à recriação.

O PostgreSQL interno fica no mesmo item `metabase-compose`, sem publicar
porta SQL. Ele guarda usuários, dashboards e configurações do Metabase.
O item `datamart-postgres` guarda os dados analíticos carregados pelo usuário.

## Persistência, backup e conferência da entrega

| Dados | Caminho na VM |
|---|---|
| PostgreSQL analítico | `/etc/easypanel/projects/datamart/datamart-postgres/data` |
| PostgreSQL interno Metabase | `/var/lib/docker/volumes/datamart_metabase-compose_metabase_db_data/_data` |
| Objetos Giftless | `/var/lib/docker/volumes/datamart_giftless_lfs-storage/_data` |
| Volume H2 anterior, preservado | `/var/lib/docker/volumes/datamart_metabase_data/_data` |
| Recuperação da configuração anterior | `/etc/datamart/archives/metabase-h2-20261123T220047Z` |

O App antigo `metabase` foi removido após autorização. Seu volume foi
preservado e a recuperação inclui `h2.tar.gz`, `easypanel-app.json` e
`volume.json`, acessíveis com sudo. A entrega tem três itens no projeto:
`datamart-postgres`, `giftless`, `metabase-compose`.

O backup Azure existente cobre o disco de SO que contém esses caminhos.
Vault `rsv-aid-prd`, política `policy-vm-daily` Enhanced, todos os discos;
última execução consultada bem-sucedida em 23/11/2026. As metas acordadas
são RPO 24 horas e RTO um dia útil, ainda sem teste de restauração.
Não remova os volumes nem execute `docker compose down -v` com dados a manter.

Foram conferidos: saúde do Metabase e seu PostgreSQL, persistência após
reinício, fonte analítica, API administrativa, autenticação SQL como
superusuário no destino privado, perfil CLI autenticado e JWT Giftless
amplo. Batch/upload/verify/download LFS e persistência do objeto sintético
foram testados durante a implantação. Os arquivos de credenciais estão com
modo `600` e proprietário `datamart-admin`.

Restam a conferência externa do login/túnel com a chave correspondente,
o teste pela VPN fora da CAMG e a entrega privada da senha Metabase escolhida
pelo responsável. A carga e organização dos dados ficam com o destinatário.
O banco analítico foi entregue sem tabelas de negócio; o objeto LFS de
validação usa o namespace `splor-mg/datamart-smoke`.
