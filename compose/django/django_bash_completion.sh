#!/usr/bin/env bash

# From https://github.com/django/django/blob/master/extras/django_bash_completion

_django_completion()
{
    COMPREPLY=( $( COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   DJANGO_AUTO_COMPLETE=1 $1 ) )
}
# When the django-admin.py deprecation ends, remove django-admin.py.
complete -F _django_completion -o default django-admin.py manage.py django-admin

_python_django_completion()
{
    if [[ ${COMP_CWORD} -ge 2 ]]; then
        local PYTHON_EXE=${COMP_WORDS[0]##*/}
        if echo "$PYTHON_EXE" | grep -qE "python([3-9]\.[0-9])?"; then
            local PYTHON_SCRIPT=${COMP_WORDS[1]##*/}
            if echo "$PYTHON_SCRIPT" | grep -qE "manage\.py|django-admin(\.py)?"; then
                COMPREPLY=( $( COMP_WORDS=( "${COMP_WORDS[*]:1}" )
                               COMP_CWORD=$(( COMP_CWORD-1 ))
                               DJANGO_AUTO_COMPLETE=1 ${COMP_WORDS[*]} ) )
            fi
        fi
    fi
}

# Support for multiple interpreters.
unset pythons
if command -v whereis &>/dev/null; then
    python_interpreters=$(whereis python | cut -d " " -f 2-)
    for python in $python_interpreters; do
        [[ $python != *-config ]] && pythons="${pythons} ${python##*/}"
    done
    unset python_interpreters
    pythons=$(echo "$pythons" | tr " " "\n" | sort -u | tr "\n" " ")
else
    pythons=python
fi

complete -F _python_django_completion -o default $pythons
unset pythons
