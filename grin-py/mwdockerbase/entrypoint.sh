#!/bin/bash

if [[ ! -z "${DEBUG_HOLD}" ]]; then
    echo "Sleeping on ENTRY"
    sleep 999999
fi


echo "Running Container"
"$@"
st=$?


if [[ ! -z "${DEBUG_HOLD}" ]]; then
    echo "Sleeping on EXIT"
    sleep 999999
fi

exit ${st}
