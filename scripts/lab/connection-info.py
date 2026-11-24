#!/usr/bin/env python3
"""Compila credenciais e URIs em arquivo privado; não imprime seus valores."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

directory = Path.home() / '.config/datamart'


def read(name):
    return json.loads((directory / name).read_text())


def connections(credentials):
    result = dict(credentials)
    user = quote(credentials['user'], safe='')
    password = quote(credentials['password'], safe='')
    database = quote(credentials['dbname'], safe='')
    prefix = f'postgresql://{user}:{password}@'
    suffix = f'/{database}?sslmode=disable'
    result['uri_internal'] = (
        prefix + f'{credentials["host"]}:{credentials["port"]}' + suffix
    )
    result['uri_ssh_tunnel'] = prefix + '127.0.0.1:15432' + suffix
    return result


result = {
    'generated_at': datetime.now(timezone.utc).isoformat(),
    'ssh': {
        'host': 'vm-aid-runtime-dev.brazilsouth.cloudapp.azure.com',
        'port': 22,
        'user': 'datamart-admin',
        'proxy': 'proxycamg.prodemge.gov.br:8080',
    },
    'postgres_admin': connections(read('postgres-admin.json')),
    'postgres_metabase_datasource': connections(
        read('postgres-analytics.json')
    ),
    'metabase': read('metabase-api-key.json'),
    'giftless': {
        'url': 'https://datamart-giftless.h0ydxp.easypanel.host',
        'lfs_url_template': 'https://datamart-giftless.h0ydxp.easypanel.host/ORG/REPO.git/info/lfs',
        'issue_token_command': (
            'lab-giftless-token --subject SEU_USUARIO --hours 8'
        ),
    },
    'easypanel': {
        'server_profile': 'datamart-lab',
        'url_on_vm': 'http://127.0.0.1:3000',
        'credentials_file': str(
            Path.home() / '.config/easypanel/credentials.json'
        ),
        'command': 'lab-easypanel',
    },
}
target = directory / 'acessos.json'
descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
os.chmod(target, 0o600)
with os.fdopen(descriptor, 'w') as output:
    json.dump(result, output, ensure_ascii=False, indent=2)
    output.write('\n')
print(f'Arquivo privado atualizado: {target}')
