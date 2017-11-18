#! /bin/bash

echo '===== RUNNING TESTS ====='

./setup.py test

echo '===== pexpect-server.log ====='
cat .pexpect-server.log
echo
echo '===== pexpect-cli.log ====='
cat .pexpect-cli.log
