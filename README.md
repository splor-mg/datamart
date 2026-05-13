# Datamart SPLOR

🇧🇷 [Português](README.pt-BR.md)

Centralized budget data platform for Minas Gerais, focused on consolidating and standardizing historical public budget data into a single PostgreSQL database.

## Context & Problem

The SPLOR Datamart project was created to organize and unify budget data from Minas Gerais, which is currently distributed across multiple repositories and data sources.

The project aims to:

- consolidate the historical budget data since 2002 into a single database;
- standardize extraction, transformation, and consolidation processes;
- reduce fragmentation and inconsistency between data sources;
- provide a reliable and centralized source of budget information.

In addition to building the database infrastructure, the project also aims to support a future self-service consultation platform, allowing users to access budget data directly without depending on technical intermediaries.

This repository is responsible for building and maintaining the database structure using Django and PostgreSQL.

## Features

- Centralizes budget data from multiple sources.
- Stores historical budget information since 2002.
- Uses Django ORM for database modeling and migrations.
- Provides administrative visualization through Django Admin.
- Uses PostgreSQL as the primary database.
- Includes development automation tasks using Taskipy.

## Prerequisites

- [Python 3.10+](https://www.python.org/).
- [Poetry](https://python-poetry.org/docs/#installation).
- [PostgreSQL](https://www.postgresql.org/download/).

## Setup

Clone the repository and install dependencies:

```bash
# clone the repo
git clone <repo-url>
cd <project>

# create env file
cp .env.example .env

# install dependencies
poetry install

# activate virtual env
eval $(poetry env activate)
```

Create the PostgreSQL database:

```bash
createdb datamart
```

Configure the `.env` file:

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

Run database migrations:

```bash
task migrate
```

Create an admin user:

```bash
python manage.py createsuperuser
```

Start the development server:

```bash
task devserver
```

The Django Admin interface will be available at:

```text
http://127.0.0.1:8000/admin/
```

## Task

To see all available project tasks:

```bash
# Need virtual environment activated
# otherwise run 'poetry run task list'
task list
```

## Available Tasks

```bash
task lint             # Checks for good coding practices in Python
task pre_format       # Applies automatic lint fixes
task format           # Formats code according to style conventions
task test             # Runs unit tests
task devserver        # Runs local development server
task makemigrations   # Creates migration files
task migrate          # Applies database migrations
```
