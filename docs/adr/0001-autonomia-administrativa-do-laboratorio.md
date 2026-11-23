---
status: accepted
---

# Autonomia administrativa do laboratório

O destinatário receberá administração completa das três ferramentas e
da máquina que as hospeda, por SSH. Essa escolha foi confirmada na rodada
de alinhamento: o usuário precisa alterar configurações e executar
comandos sozinho, ou delegá-los a uma IA, sem depender do operador para
essas tarefas. O cliente ou agente usado será escolhido pelo destinatário.

O acesso será por uma conta Linux própria, autenticada por chave SSH,
com `sudo` sem solicitar senha, conforme confirmado na rodada seguinte.
Isso permite execução administrativa não interativa pelas automações
escolhidas pelo destinatário.

Optamos por essa autonomia em vez de conceder somente acesso às APIs e
um túnel SQL, que exigiriam intervenção do operador para administrar a
instalação. A concessão efetiva depende de receber e instalar a chave
pública do destinatário; a chave privada permanece com ele.

Não serão fornecidos usuário e senha da interface do Easypanel. Isso é
diferente de uma barreira técnica contra intervenção no painel:
administração da máquina permite interferir nos processos e arquivos que
o sustentam. A administração programática do painel usará sua API/CLI
oficial, com credencial protegida na VM e compatibilidade validada antes
da entrega. Isso permite persistir configurações e reimplantar sem login
na interface. A administração da assinatura Azure e a recuperação da VM
permanecem com o operador da plataforma; não serão concedidas permissões
Azure nesta entrega.
