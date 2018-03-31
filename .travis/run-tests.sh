#! /bin/bash -x

pytest --cov nete
EXIT_CODE=$?

echo '===== pexpect-server.log ====='
cat /tmp/pexpect-server.log

exit $EXIT_CODE
