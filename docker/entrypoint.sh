#!/bin/sh
set -eu

# The platform injects FLAG as an environment variable (checker::environ).
if [ -n "${FLAG:-}" ]; then
  printf '%s\n' "${FLAG}" > /flag
else
  printf 'flag{local_test_flag}\n' > /flag
fi
chmod 400 /flag

echo "[*] ret2win listening on 0.0.0.0:9999"
exec socat TCP-LISTEN:9999,reuseaddr,fork EXEC:/pwn/vuln,stderr
