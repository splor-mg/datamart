# Datamart SPLOR

🇺🇸 [Read in English](README.md)

Plataforma centralizada de dados orçamentários de Minas Gerais, focada na consolidação e padronização de dados históricos de orçamento em um único banco PostgreSQL.

## Contexto & Problema

O projeto Datamart da SPLOR foi criado para organizar e unificar os dados orçamentários de Minas Gerais, que atualmente estão distribuídos em múltiplos repositórios e fontes de dados.

O projeto tem como objetivos:

- consolidar o histórico de dados orçamentários desde 2002 em um único banco de dados;
- padronizar os processos de extração, transformação e consolidação de dados;
- reduzir fragmentação e inconsistências entre fontes de dados;
- fornecer uma fonte confiável e centralizada de informações orçamentárias.

Além da construção da infraestrutura do banco de dados, o projeto também busca apoiar uma futura plataforma de consulta self-service, permitindo acesso direto aos dados orçamentários sem dependência de intermediários técnicos.

Este repositório é responsável pela construção e manutenção da estrutura do banco de dados utilizando Django e PostgreSQL.

## Funcionalidades

- Centraliza dados orçamentários provenientes de múltiplas fontes.
- Armazena informações históricas de orçamento desde 2002.
- Padroniza processos de extração e consolidação de dados.
- Utiliza Django ORM para modelagem e migrações do banco.
- Disponibiliza visualização administrativa através do Django Admin.
- Utiliza PostgreSQL como banco de dados principal.
- Inclui automações de desenvolvimento utilizando Taskipy.

## Pré-requisitos

- [Python 3.10+](https://www.python.org/).
- [Poetry](https://python-poetry.org/docs/#installation).
- [PostgreSQL](https://www.postgresql.org/download/).

## Configuração

Clone o repositório e instale as dependências:

```bash
# clone o repositório
git clone <repo-url>
cd <project>

# crie o arquivo de ambiente
cp .env.example .env

# instale as dependências
poetry install

# ative o ambiente virtual
eval $(poetry env activate)
```

Crie o banco PostgreSQL:

```bash
createdb datamart
```

Configure o arquivo `.env`:

```env
SECRET_KEY=1234
DEBUG=True
ALLOWED_HOSTS=

DB_NAME=datamart
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

Execute as migrações:

```bash
task migrate
```

Crie um usuário administrador:

```bash
python manage.py createsuperuser
```

Inicie o servidor de desenvolvimento:

```bash
task devserver
```

O painel administrativo do Django estará disponível em:

```text
http://127.0.0.1:8000/admin/
```

## Tasks

Para visualizar todas as tasks disponíveis no projeto:

```bash
# é necessário estar com o ambiente virtual ativado
# caso contrário utilize 'poetry run task list'
task list
```

## Tasks Disponíveis

```bash
task lint             # Verifica boas práticas de código Python
task pre_format       # Aplica correções automáticas de lint
task format           # Formata o código seguindo convenções de estilo
task test             # Executa testes automatizados
task devserver        # Inicia o servidor local de desenvolvimento
task makemigrations   # Cria arquivos de migração
task migrate          # Aplica as migrações no banco de dados
```
