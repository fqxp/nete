#! /bin/bash -x

pytest --cov nete
EXIT_CODE=$?

exit $EXIT_CODE
