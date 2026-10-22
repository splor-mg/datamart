"""Emite um JWT para um desenvolvedor; execute dentro do container Giftless."""

import argparse
import os
import time

import jwt

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    '--subject', required=True, help='Identificador do usuário'
)
parser.add_argument(
    '--scope', required=True, action='append', help='Scope LFS'
)
parser.add_argument('--hours', type=int, default=1, help='Validade, em horas')
args = parser.parse_args()
if args.hours < 1:
    parser.error('--hours deve ser maior que zero')

issued_at = int(time.time())
print(
    jwt.encode(
        {
            'sub': args.subject,
            'iat': issued_at,
            'nbf': issued_at,
            'exp': issued_at + args.hours * 3600,
            'scopes': args.scope,
        },
        os.environ['GIFTLESS_JWT_SECRET'],
        algorithm='HS256',
        headers={'kid': 'labanca-client'},
    )
)
