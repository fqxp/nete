#! /bin/bash

echo '===== RUNNING TESTS ====='

./setup.py test
EXIT_CODE=$?

echo '===== pexpect-server.log ====='
cat /tmp/pexpect-server.log
echo

exit $EXIT_CODE
