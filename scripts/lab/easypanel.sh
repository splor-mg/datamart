#!/bin/sh
set -eu

export EASYPANEL_CREDENTIALS_FILE="${EASYPANEL_CREDENTIALS_FILE:-$HOME/.config/easypanel/credentials.json}"
exec /usr/local/bin/easypanel --server datamart-lab "$@"
