# Senhas, chaves e tokens do laboratório Datamart

Inventário da entrega, conferido em 23/11/2026 e atualizado em 24/11/2026.
Esta página pode ser
compartilhada com o administrador do laboratório e seu agente de IA.
Ela registra onde obter as credenciais; os valores ficam nos arquivos
privados e nos ambientes dos serviços.

O [guia de operação](operacao-laboratorio.md) contém endereços, comandos,
túnel SQL, APIs, persistência e procedimentos de manutenção. O acesso
administrativo às ferramentas e à VM é completo; não será entregue
usuário e senha da interface web do Easypanel.

## Credenciais necessárias para acessar

Os caminhos iniciados por `~` nesta tabela pertencem à conta Linux
`datamart-admin` na VM `vm-aid-runtime-dev`:
`~` corresponde a `/home/datamart-admin`.

| Acesso | Credencial | Onde está disponível hoje |
|---|---|---|
| Metabase web | E-mail e senha da conta global | O responsável guardou no `.env` do repositório em sua máquina local, nas variáveis `METABASE_ADMIN_USERNAME` e `METABASE_ADMIN_PASSWORD`. Deve repassá-los por canal privado. |
| Metabase por API/IA | API key administrativa, grupo `Administrators` | Na VM: `~/.config/datamart/metabase-api-key.json`. Também consta em `acessos.json`. |
| PostgreSQL analítico em cliente SQL | Usuário `postgres` e senha de superusuário | Na VM: `~/.config/datamart/postgres-admin.json`. As URIs completas estão em `acessos.json`. Use o túnel SSH descrito no guia. |
| Giftless / Git LFS | JWT usado como senha pelo cliente LFS | O administrador gera pela VM com `lab-giftless-token`; não depende de uma senha fixa nem do login no painel. |
| SSH da VM | Chave privada correspondente à pública autorizada | A chave pública enviada pela destinatária foi autorizada para `datamart-admin` em 24/11/2026, preservando a chave do responsável. A privada permanece na máquina da destinatária. |
| Proxy CAMG e VPN corporativa | Credenciais corporativas do próprio destinatário | Devem estar disponíveis com o usuário. Não foram criadas nem armazenadas pela implantação do laboratório. |
| Gestão pelo Easypanel CLI | Token administrativo da API dev | Na VM: `~/.config/easypanel/credentials.json`, perfil `datamart-lab`, usado pelo comando `lab-easypanel`. |

A conta SSH `datamart-admin` autentica por chave, sem senha da VM. Seu
`sudo` está configurado para não pedir senha. Caso a chave privada tenha
passphrase, o cliente SSH poderá solicitá-la separadamente; ela pertence
ao titular da chave.

Na VM, `lab-postgres` abre `psql` como superusuário sem solicitar a senha
SQL, usando o acesso administrativo local ao container. Já um cliente SQL
externo, por túnel, usa as credenciais de `postgres-admin.json`.

O `.env` local está ignorado pelo Git e não acompanha um clone em outro
computador. Os campos de login Metabase estavam preenchidos na conferência;
seus valores não foram incluídos nesta documentação. A senha desse login
é diferente das senhas do banco interno do Metabase.

## Arquivo consolidado de acesso na VM

```text
/home/datamart-admin/.config/datamart/acessos.json
```

Esse arquivo contém os endereços, as credenciais SQL administrativas e
técnicas, as URIs PostgreSQL para rede Docker e túnel local, a API key
Metabase, o comando para emitir JWT Giftless e a referência ao perfil CLI.
A senha de login web Metabase, a chave SSH privada e a senha corporativa
do proxy não estão nessa compilação.

Os arquivos JSON de credenciais na VM foram conferidos com modo `600`,
pertencentes a `datamart-admin`. Após entrar por SSH, o usuário ou seu
agente pode consumi-los diretamente para executar os comandos e acessar
as APIs. Não copie os valores para Git, tickets ou prompts.

Para atualizar a compilação depois de atualizar os arquivos individuais:

```sh
lab-connection-info
```

O comando recompila os arquivos; não rotaciona credenciais nem consulta
automaticamente novos valores nos serviços.

## Emitir a credencial Giftless

Na sessão SSH da VM, substitua `SEU_USUARIO` por um identificador do
destinatário:

```sh
umask 077
lab-giftless-token --subject SEU_USUARIO --hours 8 \
  > "$HOME/.config/datamart/giftless.jwt"
```

O JWT tem oito horas de validade e escopo amplo
`obj:*/*/*:read,write,verify`. Quando expirar, o administrador pode emitir
outro. No cliente Git LFS, o usuário Basic é `_jwt` e a senha é esse JWT;
clientes API também podem usar `Authorization: Bearer TOKEN`. O arquivo
gerado deve ser entregue ou consumido por um canal privado, sem inserir
o token na URL do repositório.

## Credenciais internas para manutenção

Estas credenciais já estão configuradas nos ambientes dos serviços. O
administrador poderá consultá-las pela CLI/SSH quando precisar administrar
ou alterar a instalação:

| Serviço | Credencial ou segredo | Uso |
|---|---|---|
| PostgreSQL analítico | Role técnica `datamart`; arquivo `~/.config/datamart/postgres-analytics.json` | Identidade proprietária do banco `datamart`, usada pela fonte analítica do Metabase. |
| PostgreSQL interno do Metabase | `METABASE_POSTGRES_ADMIN_PASSWORD` | Senha do superusuário da instância que guarda os dados da aplicação. |
| Aplicação Metabase | `METABASE_DB_PASSWORD` | Senha da role técnica `metabase` para seu banco interno. |
| Aplicação Metabase | `METABASE_ENCRYPTION_SECRET_KEY` | Chave de criptografia da aplicação; deve ser preservada entre deploys. |
| Giftless | `GIFTLESS_JWT_SECRET` e `GIFTLESS_INTERNAL_SECRET` | Segredos de assinatura usados pela instalação. |

As três variáveis do Metabase ficam no ambiente do item `metabase-compose`;
as duas do Giftless ficam no ambiente do item `giftless`. Elas não são
senhas de login web. Para operações administrativas rotineiras, os comandos
instalados e a CLI já utilizam as credenciais necessárias.

O token antigo da API Easypanel dev foi substituído nesta entrega.
Clientes que utilizavam o token anterior precisam atualizar sua credencial.
Ao trocar senhas ou segredos, atualize também os serviços dependentes e
os arquivos privados de acesso.

## O que o responsável precisa entregar

1. Os links desta página e do [guia de operação](operacao-laboratorio.md).
2. E-mail e senha Metabase, por canal privado.
3. Acesso SSH: a chave pública da destinatária já está autorizada. Ela mantém
   sua própria chave privada; não deve enviá-la ao responsável.
4. Confirmação de que o destinatário dispõe das credenciais corporativas
   e alcança o proxy CAMG, pela rede corporativa ou VPN.

Depois do primeiro login SSH, as demais credenciais necessárias estarão
disponíveis nos arquivos protegidos da VM. Ainda precisa ser conferido
externamente o login/túnel do destinatário com sua chave e a conectividade
pela VPN fora da CAMG.
