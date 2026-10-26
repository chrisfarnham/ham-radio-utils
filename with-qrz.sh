#!/usr/bin/env bash
# Optional helper: run a command with QRZ credentials taken from LastPass.
#
#   ./with-qrz.sh ./enrich-adif.py "file.adi" --apply
#
# Nothing in this repo requires it. enrich-adif.py reads qrz_username and
# qrz_password from the environment or from a .env file; this script is only for
# keeping them in LastPass instead of on disk. It needs the lastpass-cli
# (`brew install lastpass-cli`) and a secure note whose body is KEY=value lines:
#
#   qrz_username=W1YTQ
#   qrz_password='quote values containing spaces, $ or #'
#
# The note name defaults to ham-radio-utils/qrz; override with QRZ_LPASS_NOTE.
# The values are exported to the one command only and never written to disk.

set -euo pipefail

NOTE="${QRZ_LPASS_NOTE:-ham-radio-utils/qrz}"

if [ "$#" -eq 0 ]; then
    echo "usage: $0 <command> [args...]" >&2
    exit 2
fi
if ! command -v lpass >/dev/null 2>&1; then
    echo "with-qrz.sh: lpass not found; install lastpass-cli or use a .env file instead" >&2
    exit 1
fi
if ! lpass status -q; then
    echo "with-qrz.sh: not logged in to LastPass; run 'lpass login <email>'" >&2
    exit 1
fi

creds=$(lpass show --notes "$NOTE") || {
    echo "with-qrz.sh: could not read LastPass note '$NOTE'" >&2
    exit 1
}

set -a
# shellcheck disable=SC1091
source /dev/stdin <<<"$creds"
set +a
exec "$@"
