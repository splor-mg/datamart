#!/usr/bin/env python3
"""Cliente administrativo Metabase; a chave é lida de arquivo privado na VM."""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('method', choices=['GET', 'POST', 'PUT', 'DELETE'])
parser.add_argument('path', help='Caminho /api/...')
parser.add_argument('--input', help='JSON em arquivo, ou - para stdin')
args = parser.parse_args()
if not args.path.startswith('/api/'):
    parser.error('Use um caminho iniciado por /api/.')
credentials_path = Path(
    os.environ.get(
        'METABASE_CREDENTIALS_FILE',
        str(Path.home() / '.config/datamart/metabase-api-key.json'),
    )
)
credentials = json.loads(credentials_path.read_text(encoding='utf-8'))
data = None
if args.input:
    text = (
        sys.stdin.read()
        if args.input == '-'
        else Path(args.input).read_text(encoding='utf-8')
    )
    data = json.dumps(json.loads(text)).encode()
request = urllib.request.Request(
    credentials['url'] + args.path,
    data=data,
    method=args.method,
    headers={
        'X-API-Key': credentials['api_key'],
        'Content-Type': 'application/json',
    },
)
try:
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read()
        if body:
            print(json.dumps(json.loads(body), ensure_ascii=False, indent=2))
except urllib.error.HTTPError as error:
    raise SystemExit(f'Metabase respondeu HTTP {error.code}.') from None
