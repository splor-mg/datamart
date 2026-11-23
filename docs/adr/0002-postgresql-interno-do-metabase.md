---
status: accepted
---

# PostgreSQL interno separado para o Metabase

O banco de configuração do Metabase terá uma instância PostgreSQL própria,
agrupada com a aplicação em um único item Compose no Easypanel. O
PostgreSQL analítico permanece como outro item do projeto. Essa organização
foi confirmada pelo usuário na rodada de alinhamento.

A alternativa era manter dois bancos na mesma instância PostgreSQL.
Escolhemos a separação para distinguir manutenção, dados persistentes e
recuperação da configuração da aplicação dos experimentos analíticos,
preservando a organização funcional em três itens no painel. A conta
técnica da aplicação é diferente da conta administrativa do destinatário.
