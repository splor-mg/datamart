# Acesso SSH ao laboratório pela CAMG

O acesso à VM foi definido e aplicado no projeto `azure-migration`.
Esta página adapta o procedimento para o administrador do laboratório,
sem reproduzir as credenciais ou os caminhos de chave do operador atual.

| Item | Configuração |
|---|---|
| VM | `vm-aid-runtime-dev.brazilsouth.cloudapp.azure.com` |
| SSH | TCP/22 |
| Proxy corporativo | `proxycamg.prodemge.gov.br:8080` |
| Origem permitida pelo NSG | `200.198.60.112/32`, saída pública do proxy |
| Regra | `AllowSSHFromCAMG`, prioridade 300, no `nsg-aid-runtime-dev` |
| Rede do cliente | Rede corporativa CAMG; fora dela, VPN corporativa para alcançar o proxy |
| Autenticação no proxy | Usuário e senha corporativos do destinatário |
| Autenticação na VM | Conta Linux autorizada e sua chave SSH privada |

Conforme a auditoria de 23/11/2026, a regra foi aplicada com sucesso,
persistida no Bicep e conferida no NSG da subnet dev. O responsável
confirmou uma sessão SSH interativa pela CAMG como `aidadmin`. O acesso
pela VPN de casa ainda precisa ser validado.

O login administrativo existente é `aidadmin`. A conta `datamart-admin`
foi criada em 23/11/2026, com a chave pública fornecida pelo responsável:
`SHA256:HDb9ELZoNI1Mp9R62k7A+TXw24yAF/jsobpZyB8ObLU` (ED25519).
Foram validados UID 1001, execução de sudo sem senha como root e a
configuração efetiva SSH: chave pública habilitada, senha e autenticação
interativa desabilitadas, shell/TTY e encaminhamento TCP permitidos.
O login externo dessa conta ainda precisa ser conferido com a chave privada
correspondente. O acesso administrativo completo segue a
[decisão do laboratório](adr/0001-autonomia-administrativa-do-laboratorio.md).

## Conectar pelo Git Bash

O Git Bash deve disponibilizar `ssh` e `connect`. Preencha as três variáveis
com seus dados autorizados. Use a chave privada em `ssh -i`; o arquivo
`.pub` é usado pelo operador para autorizar essa chave na VM.

```bash
(
  CAMG_PROXY_USER=SEU_USUARIO_CAMG
  LAB_SSH_USER=SEU_USUARIO_LINUX_AUTORIZADO
  LAB_SSH_KEY="$HOME/.ssh/SUA_CHAVE_PRIVADA"

  read -rsp 'Senha do proxy CAMG: ' HTTP_PROXY_PASSWORD
  printf '\n'
  export HTTP_PROXY_PASSWORD

  ssh -i "$LAB_SSH_KEY" \
    -o IdentitiesOnly=yes \
    -o "ProxyCommand=connect -H ${CAMG_PROXY_USER}@proxycamg.prodemge.gov.br:8080 %h %p" \
    "${LAB_SSH_USER}@vm-aid-runtime-dev.brazilsouth.cloudapp.azure.com"
)
```

A senha solicitada é a do proxy. A VM autentica pela chave SSH; se ela
tiver passphrase, haverá uma solicitação separada. O subshell mantém a
variável da senha apenas durante a sessão. Cada administrador usa suas
próprias credenciais; senhas e chaves privadas ficam fora do Git e do chat.

O administrador pode executar comandos manualmente ou por sua ferramenta
de IA através do SSH. O cliente precisa alcançar o proxy e dispor das
credenciais autorizadas. Uma sessão SSH aberta permite executar os
[comandos SQL e de gestão](easypanel-acesso-e-compose.md#comandos-sql-com-a-administração-ssh)
na VM, com as permissões administrativas decididas para o laboratório.

## Diagnóstico

| Mensagem | Conferir |
|---|---|
| `407 Proxy Authentication Required` | Credenciais e método de autenticação do proxy |
| `502 cannotconnect` | Permissão CONNECT para 22, saída do proxy e regra Azure |
| `Permission denied (publickey)` | Conta Linux e correspondência entre chave privada e pública autorizada |
| `UNKNOWN port 65535` | Erro anterior do auxiliar `connect`; o canal do proxy foi perdido |

Use `ssh -vv` e `connect -d` quando precisar diagnosticar. Compartilhe
somente as mensagens relevantes, removendo senhas e `Proxy-Authorization`.

## Fontes e responsabilidade

Fontes consultadas no projeto `azure-migration`:

- `docs/18-acesso-ssh-dev.md`: procedimento administrativo e confirmação do login;
- `auditoria/2026-11-23/ACESSO-SSH-DEV.md`: aplicação e verificação da regra Azure.

Esses registros são a evidência desta atualização; não foi realizado
outro login SSH pelo agente do Datamart. A regra de rede é mantida pelo
`azure-migration`, sem reaplicar ou duplicar o Bicep neste repositório.
