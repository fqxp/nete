#! /bin/bash

echo '===== RUNNING TESTS ====='

pytest
EXIT_CODE=$?

echo '===== pexpect-server.log ====='
cat /tmp/pexpect-server.log
echo

exit $EXIT_CODE
