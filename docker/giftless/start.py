"""Configura as chaves em runtime e preserva tini/uWSGI da imagem oficial."""

import json
import os
import sys
from pathlib import Path

import yaml

required_keys = ('GIFTLESS_JWT_SECRET', 'GIFTLESS_INTERNAL_SECRET')
for key in required_keys:
    if not os.environ.get(key):
        sys.exit(f'Defina {key} no ambiente do serviço Giftless')

config = yaml.safe_load(
    Path('/app/giftless-config.yaml').read_text(encoding='utf-8')
)
config['AUTH_PROVIDERS'][0]['options']['private_key'] = os.environ[
    'GIFTLESS_JWT_SECRET'
]
config['PRE_AUTHORIZED_ACTION_PROVIDER']['options']['private_key'] = (
    os.environ['GIFTLESS_INTERNAL_SECRET']
)
os.environ['GIFTLESS_CONFIG_STR'] = json.dumps(config)
os.execvp('tini', ['tini', '--', 'uwsgi', *sys.argv[1:]])
