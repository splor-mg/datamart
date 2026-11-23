"""Cria o primeiro administrador pela rede privada, com senha no TTY."""

import argparse
import getpass
import ipaddress
import json
import socket
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group()
    target.add_argument(
        '--url', help='URL HTTP privada, acessível deste container'
    )
    target.add_argument(
        '--container',
        default='datamart_metabase-compose-metabase-1',
        help='Container local; usa docker exec e o curl da imagem Metabase',
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if not sys.stdin.isatty():
        sys.exit(
            'Execute em terminal interativo; '
            'não forneça senha por pipe ou argumento.'
        )

    if args.url:
        url = urllib.parse.urlsplit(args.url)
        if (
            url.scheme != 'http'
            or not url.hostname
            or url.username
            or url.password
        ):
            sys.exit('--url deve ser HTTP privado, sem credenciais na URL.')
        addresses = socket.getaddrinfo(url.hostname, url.port or 80)
        if not all(
            ipaddress.ip_address(item[4][0]).is_private for item in addresses
        ):
            sys.exit(
                'O assistente só aceita endereço privado; '
                'não publique o setup aberto.'
            )

    def request(path, payload=None):
        body = None if payload is None else json.dumps(payload).encode()
        if args.url:
            req = urllib.request.Request(
                args.url.rstrip('/') + path,
                data=body,
                headers={'Content-Type': 'application/json'},
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    return json.load(response)
            except urllib.error.HTTPError as error:
                sys.exit(
                    f'Metabase recusou a solicitação (HTTP {error.code}). '
                    'Revise os dados.'
                )
        command = [
            'docker',
            'exec',
            '-i',
            args.container,
            'curl',
            '--silent',
            '--show-error',
            '--max-time',
            '30',
            '--write-out',
            chr(10) + '%{http_code}',
        ]
        if body is not None:
            command += [
                '--header',
                'Content-Type: application/json',
                '--data-binary',
                '@-',
            ]
        command.append('http://localhost:3000' + path)
        result = subprocess.run(
            command, input=body, capture_output=True, timeout=40, check=False
        )
        if result.returncode:
            sys.exit(
                'Não foi possível alcançar o Metabase '
                'pelo container informado.'
            )
        response_body, status = result.stdout.rsplit(bytes([10]), 1)
        if status != b'200':
            sys.exit(
                f'Metabase recusou a solicitação (HTTP {status.decode()}). '
                'Revise os dados.'
            )
        return json.loads(response_body)

    properties = request('/api/session/properties')
    token = properties.get('setup-token')
    if not token:
        sys.exit(
            'O setup já foi concluído. '
            'Este comando não altera contas ou senhas existentes.'
        )
    print(
        'Criação da primeira conta administrativa do Metabase, '
        'ainda sem rota pública.'
    )
    first_name = input('Nome: ').strip()
    last_name = input('Sobrenome: ').strip()
    email = input('E-mail da conta: ').strip()
    site_name = input('Nome da instalação [Datamart]: ').strip() or 'Datamart'
    password = getpass.getpass('Senha (não será exibida): ')
    if password != getpass.getpass('Confirme a senha: '):
        sys.exit('As senhas não coincidem; nenhuma conta foi criada.')
    if not first_name or not last_name or not email or not password:
        sys.exit('Preencha todos os dados; nenhuma conta foi criada.')
    confirmation = input(
        'Criar esta conta com administração global? [sim/N]: '
    )
    if confirmation.strip().lower() != 'sim':
        sys.exit('Cancelado; nenhuma conta foi criada.')
    request(
        '/api/setup',
        {
            'token': token,
            'user': {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'password': password,
            },
            'prefs': {
                'site_name': site_name,
                'site_locale': 'pt-BR',
                'allow_tracking': False,
            },
        },
    )
    if request('/api/session/properties').get('setup-token'):
        sys.exit(
            'Não foi possível confirmar o encerramento do setup; '
            'mantenha a rota privada.'
        )
    print(
        'Administrador criado e setup encerrado. '
        'A rota HTTPS pode ser configurada.'
    )


if __name__ == '__main__':
    main()
