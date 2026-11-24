#!/usr/bin/env python3
"""Descobre o endereço privado atual do PostgreSQL alcançável pela VM."""

import ipaddress
import json
import re
import socket
import subprocess


def docker_json(*arguments):
    return json.loads(
        subprocess.check_output(['docker', *arguments], text=True)
    )


container = subprocess.check_output(
    [
        'docker',
        'ps',
        '-q',
        '--filter',
        'label=com.docker.swarm.service.name=datamart_datamart-postgres',
    ],
    text=True,
).strip()
if not container or '\n' in container:
    raise SystemExit('Aguarde uma única instância saudável do PostgreSQL.')
details = docker_json('inspect', container)[0]
bridge = docker_json('network', 'inspect', 'docker_gwbridge')[0]
subnets = [
    ipaddress.ip_network(config['Subnet'])
    for config in bridge['IPAM']['Config']
    if ':' not in config['Subnet']
]
addresses = subprocess.check_output(
    [
        'nsenter',
        '-t',
        str(details['State']['Pid']),
        '-n',
        'ip',
        '-o',
        '-4',
        'addr',
        'show',
    ],
    text=True,
)
target = next(
    (
        address
        for address in re.findall(r'inet ([0-9.]+)/', addresses)
        if any(ipaddress.ip_address(address) in subnet for subnet in subnets)
    ),
    None,
)
if not target:
    raise SystemExit('Endereço docker_gwbridge do PostgreSQL não encontrado.')
with socket.create_connection((target, 5432), timeout=5):
    print(target)
